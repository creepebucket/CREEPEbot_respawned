import io
import json
import os
import time
from typing import List, Dict, Tuple

import xxhash
import zstandard as zstd

# 假设这是一个 MongoDB 的集合，用于存储备份历史的元数据
from lib.database import backup_collection

# 定义备份系统使用的常量
BACKUP_DIRNAME = '.creepe_backup'  # 备份根目录名
BLOB_DIRNAME = 'blobs'  # 存放压缩后的文件数据块目录
MANIFEST_DIRNAME = 'manifests'  # 存放备份清单（JSON）目录
ZSTD_LEVEL = 3  # Zstandard 压缩等级


def _get_backup_paths(dir: str) -> Tuple[str, str, str, str]:
    """根据传入的目标目录，计算并返回所有相关的绝对路径"""
    abs_dir = os.path.abspath(dir)
    backup_root = os.path.join(abs_dir, BACKUP_DIRNAME)
    blob_dir = os.path.join(backup_root, BLOB_DIRNAME)
    manifest_dir = os.path.join(backup_root, MANIFEST_DIRNAME)
    return abs_dir, backup_root, blob_dir, manifest_dir


def _iter_files(abs_dir: str):
    """
    遍历目录下的所有文件。
    使用生成器产出文件的绝对路径和相对路径，并自动跳过备份目录本身。
    """
    for root, dirs, files in os.walk(abs_dir):
        # 核心逻辑：如果在当前层级发现了备份目录，将其从遍历列表中移除，避免陷入死循环或备份了备份文件
        if BACKUP_DIRNAME in dirs:
            dirs.remove(BACKUP_DIRNAME)
        for file_name in files:
            abs_path = os.path.join(root, file_name)
            # 计算相对路径，并将路径分隔符统一替换为 '/'（跨平台兼容性）
            rel_path = os.path.relpath(abs_path, abs_dir).replace(os.sep, '/')
            yield abs_path, rel_path


def _read_manifest(manifest_path: str) -> Dict:
    """读取并解压 ZSTD 压缩的 JSON 清单文件"""
    with open(manifest_path, 'rb') as f:
        with zstd.ZstdDecompressor().stream_reader(f) as reader:
            data = reader.read()
    return json.loads(data.decode('utf-8'))


def start_backup(dir: str, name: str):
    """执行目录备份的主逻辑"""
    current_time = time.time_ns()  # 使用纳秒级时间戳作为唯一标识

    # 准备元数据和目录
    metadata = {'name': str(current_time) if name is None else name, 'time': current_time}
    abs_dir, _, blob_dir, manifest_dir = _get_backup_paths(dir)
    os.makedirs(blob_dir, exist_ok=True)
    os.makedirs(manifest_dir, exist_ok=True)

    # 尝试获取上一次的备份记录，用于实现增量备份（加速）
    prev_doc = backup_collection.find_one({'source_dir': abs_dir}, sort=[('time', -1)])
    prev_files = {}
    if prev_doc is not None:
        # 如果存在旧备份，读取它的清单，生成 {相对路径: 文件信息} 的字典
        prev_manifest = _read_manifest(prev_doc['manifest_path'])
        prev_files = {item['path']: item for item in prev_manifest['files']}

    # 统计数据初始化
    total_bytes = 0
    reused_files = 0
    changed_files = 0
    backup_files = []

    # 遍历当前目录下的所有文件
    for abs_path, rel_path in _iter_files(abs_dir):
        stat = os.stat(abs_path)
        size = stat.st_size
        mtime_ns = stat.st_mtime_ns  # 文件的纳秒级最后修改时间
        total_bytes += size

        prev = prev_files.get(rel_path)
        # 增量备份核心逻辑（快路径）：如果文件大小和修改时间都没变，认为内容没变
        if prev is not None and prev['size'] == size and prev['mtime_ns'] == mtime_ns:
            file_hash = prev['hash']  # 直接复用旧哈希，不读取文件内容
            reused_files += 1
        else:
            # 文件发生了改变或者是新文件（慢路径），计算文件的 xxhash64 摘要
            hasher = xxhash.xxh3_64()
            with open(abs_path, 'rb') as f:
                # 分块读取，防止大文件撑爆内存 (每次 1MB)
                for chunk in iter(lambda: f.read(1024 * 1024), b''):
                    hasher.update(chunk)
            file_hash = hasher.hexdigest()
            changed_files += 1

            # 去重机制：检查由哈希命名的 blob 是否已存在，如果不存在才进行压缩存储
            blob_path = os.path.join(blob_dir, f'{file_hash}.zst')
            if not os.path.exists(blob_path):
                with open(abs_path, 'rb') as src, open(blob_path, 'wb') as dst:
                    zstd.ZstdCompressor(level=ZSTD_LEVEL).copy_stream(src, dst)

        # 记录该文件在本次备份中的状态
        backup_files.append({'path': rel_path, 'size': size, 'mtime_ns': mtime_ns, 'hash': file_hash})

    # 构建本次备份的清单 (Manifest)
    manifest_path = os.path.join(manifest_dir, f'{current_time}.json.zst')
    manifest = {'version': 1, 'time': current_time, 'name': metadata['name'], 'source_dir': abs_dir,
                'files': backup_files}

    # 将清单压缩后写入磁盘
    with open(manifest_path, 'wb') as f:
        with zstd.ZstdCompressor(level=ZSTD_LEVEL).stream_writer(f) as writer:
            with io.TextIOWrapper(writer, encoding='utf-8') as text:
                # 使用 separators=(',', ':') 移除多余空格，缩小 JSON 体积
                json.dump(manifest, text, ensure_ascii=False, separators=(',', ':'))

    # 构建要写入数据库的摘要文档
    backup_doc = {
        'source_dir': abs_dir,
        'time': current_time,
        'name': metadata['name'],
        'manifest_path': manifest_path,
        'file_count': len(backup_files),
        'total_bytes': total_bytes,
        'changed_files': changed_files,
        'reused_files': reused_files,
    }
    # 写入数据库并返回
    backup_collection.insert_one(backup_doc)
    return backup_doc


def list_backup(dir: str) -> List[Dict]:
    """查询指定目录的历史备份列表"""
    abs_dir, _, _, _ = _get_backup_paths(dir)
    # 按时间倒序查询数据库，过滤掉内部字段（_id, source_dir, manifest_path）
    docs = backup_collection.find(
        {'source_dir': abs_dir},
        {'_id': 0, 'source_dir': 0, 'manifest_path': 0},
    ).sort('time', -1)
    return list(docs)


def restore_backup(dir: str, time: int):
    """将目录恢复到指定时间戳的状态"""
    abs_dir, _, blob_dir, manifest_dir = _get_backup_paths(dir)
    manifest_path = os.path.join(manifest_dir, f'{time}.json.zst')

    # 读取对应时间的清单文件
    manifest = _read_manifest(manifest_path)
    # 提取当时存在的所有文件的相对路径
    want_files = {item['path'] for item in manifest['files']}

    # 清理阶段：遍历当前目录，删除所有不在历史清单中的多余文件
    for abs_path, rel_path in _iter_files(abs_dir):
        if rel_path not in want_files:
            os.remove(abs_path)

    # 恢复阶段：遍历历史清单中的每一个文件
    for item in manifest['files']:
        # 将相对路径转换回当前系统的绝对路径格式
        abs_path = os.path.join(abs_dir, item['path'].replace('/', os.sep))
        # 确保文件的父目录存在
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)

        # 根据哈希值找到对应的压缩数据块
        blob_path = os.path.join(blob_dir, f"{item['hash']}.zst")
        # 将数据块解压缩写回原本的文件路径
        with open(blob_path, 'rb') as src, open(abs_path, 'wb') as dst:
            zstd.ZstdDecompressor().copy_stream(src, dst)

        # 极为关键的一步：将恢复出来的文件修改时间（mtime）改回当时的时间。
        # 这样下次执行 start_backup 时，增量备份逻辑（根据 mtime 判断）才能正常工作。
        os.utime(abs_path, ns=(item['mtime_ns'], item['mtime_ns']))

    return True
