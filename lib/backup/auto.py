import asyncio
import os
import re
import time

from lib import logger
from lib.backup import start_backup, list_backup, BACKUP_DIRNAME, MANIFEST_DIRNAME
from lib.database import backup_collection
from lib.database.config import global_config
from lib.mcsmanager.instance import get_instance_cwd_by_nickname, get_instance_detail_by_nickname, get_output_log_by_nickname


def get_auto_backup_tasks():
    return global_config.get('auto_backup/tasks', [])


def set_auto_backup_tasks(tasks):
    global_config.set('auto_backup/tasks', tasks)


def upsert_auto_backup_task(nickname: str, enabled: bool, interval_min: int, keep: int, prefix: str):
    tasks = get_auto_backup_tasks()

    for task in tasks:
        if task['nickname'] != nickname:
            continue

        task['enabled'] = enabled
        task['interval_min'] = interval_min
        task['keep'] = keep
        task['prefix'] = prefix
        if enabled:
            task['next_time'] = int(time.time())
        set_auto_backup_tasks(tasks)
        return task

    task = {
        'nickname': nickname,
        'enabled': enabled,
        'interval_min': interval_min,
        'keep': keep,
        'prefix': prefix,
        'next_time': int(time.time()) if enabled else 0,
    }
    tasks.append(task)
    set_auto_backup_tasks(tasks)
    return task


def set_auto_backup_enabled(nickname: str, enabled: bool):
    tasks = get_auto_backup_tasks()
    for task in tasks:
        if task['nickname'] != nickname:
            continue

        task['enabled'] = enabled
        task['next_time'] = int(time.time()) if enabled else 0
        set_auto_backup_tasks(tasks)
        return task

    task = {
        'nickname': nickname,
        'enabled': enabled,
        'interval_min': 60,
        'keep': 24,
        'prefix': 'auto',
        'next_time': int(time.time()) if enabled else 0,
    }
    tasks.append(task)
    set_auto_backup_tasks(tasks)
    return task


def get_auto_backup_task(nickname: str):
    tasks = get_auto_backup_tasks()
    for task in tasks:
        if task['nickname'] == nickname:
            return task
    return None


def get_online_player_count(nickname: str) -> int:
    detail = get_instance_detail_by_nickname(nickname)
    current_players = detail['data']['info'].get('currentPlayers', -1)
    if current_players >= 0:
        return current_players

    log_resp = get_output_log_by_nickname(nickname)
    log_text = log_resp['data']
    match = re.search(r'There are (\d+) of a max of \d+ players online', log_text)
    if match:
        return int(match.group(1))
    return 0


def format_auto_backup_task(task):
    if task is None:
        return '未配置自动备份'

    return (f'实例: {task["nickname"]}\n'
            f'状态: {"开启" if task["enabled"] else "关闭"}\n'
            f'间隔: {task["interval_min"]} 分钟\n'
            f'保留: {task["keep"]} 个\n'
            f'前缀: {task["prefix"]}\n'
            f'下次: {task["next_time"]}')


async def run_auto_backup_now(nickname: str):
    task = get_auto_backup_task(nickname)
    if task is None:
        task = set_auto_backup_enabled(nickname, False)

    cwd = await asyncio.to_thread(get_instance_cwd_by_nickname, nickname)
    backup_name = f'{task["prefix"]} {time.strftime("%Y-%m-%d %H:%M:%S")}'
    doc = await asyncio.to_thread(start_backup, cwd, backup_name)

    keep = task['keep']
    if keep > 0:
        backups = await asyncio.to_thread(list_backup, cwd)
        for old in backups[keep:]:
            abs_dir = os.path.abspath(cwd)
            manifest_path = os.path.join(abs_dir, BACKUP_DIRNAME, MANIFEST_DIRNAME, f'{old["time"]}.json.zst')
            os.remove(manifest_path)
            backup_collection.delete_one({'source_dir': abs_dir, 'time': old['time']})

    next_time = int(time.time()) + int(task['interval_min']) * 60
    tasks = get_auto_backup_tasks()
    for i in tasks:
        if i['nickname'] == nickname:
            i['next_time'] = next_time
            break
    set_auto_backup_tasks(tasks)
    return doc


async def _auto_backup_loop():
    await asyncio.sleep(2)

    while True:
        now = int(time.time())
        tasks = get_auto_backup_tasks()

        for task in tasks:
            if not task.get('enabled', False):
                continue
            if now < int(task.get('next_time', 0)):
                continue

            nickname = task['nickname']
            logger.info(f'自动备份触发: {nickname}')
            try:
                online_count = await asyncio.to_thread(get_online_player_count, nickname)
                if online_count <= 0:
                    logger.info(f'自动备份跳过: {nickname} 没有在线玩家')
                    next_time = int(time.time()) + int(task['interval_min']) * 60
                    tasks = get_auto_backup_tasks()
                    for t in tasks:
                        if t['nickname'] == nickname:
                            t['next_time'] = next_time
                            break
                    set_auto_backup_tasks(tasks)
                    continue

                doc = await run_auto_backup_now(nickname)
                logger.info(f'自动备份完成: {nickname} {doc["time"]} {doc["name"]}')
            except Exception as e:
                logger.error(f'自动备份失败: {nickname} {type(e).__name__}: {e}')

        await asyncio.sleep(10)


async def start_auto_backup():
    logger.info('自动备份任务已启动')
    asyncio.create_task(_auto_backup_loop())
