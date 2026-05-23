from typing import Dict, List, Optional

from lib.mcsmanager import api


@api('GET', 'api/files/list')
def get_file_list(daemonId: str, uuid: str, target: str = '/', page: int = 0, page_size: int = 100) -> Dict:
    """
    获取文件列表.

    返回示例:
    {
      "status": 200,
      "data": {
        "items": [
          {
            "name": "Genshin Impact",
            "size": 0,    // byte
            "time": "Fri Jun 07 2024 08:53:34 GMT+0800 (中国标准时间)",
            "mode": 777, // Linux file permission
            "type": 0 // 0 = Folder, 1 = File
          },
          {
            "name": "NEKO-MIMI SWEET HOUSEMATES Vol. 1",
            "size": 0,
            "time": "Thu Jun 06 2024 18:25:14 GMT+0800 (中国标准时间)",
            "mode": 777,
            "type": 0
          },
          {
            "name": "Poly Bridge",
            "size": 0,
            "time": "Thu Jun 06 2024 18:25:14 GMT+0800 (中国标准时间)",
            "mode": 777,
            "type": 0
          },
          {
            "name": "Wuthering Waves",
            "size": 0,
            "time": "Fri Jun 07 2024 04:32:58 GMT+0800 (中国标准时间)",
            "mode": 666,
            "type": 0
          },
          {
            "name": "AngryBirdsSeasons",
            "size": 0,
            "time": "Thu Jun 06 2024 18:25:14 GMT+0800 (中国标准时间)",
            "mode": 777,
            "type": 0
          },
          {
            "name": "secret base_君がくれたもの【Covered by Kotoha】.mp4",
            "size": 13253857,
            "time": "Thu Jun 06 2024 19:37:35 GMT+0800 (中国标准时间)",
            "mode": 666,
            "type": 1
          }
        ],
        "page": 0,
        "pageSize": 100,
        "total": 6,
        "absolutePath": "\\"
      },
      "time": 1718594177859
    }
    """


@api('PUT', 'api/files/', query_keys=['daemonId', 'uuid'])
def get_file_content(daemonId: str, uuid: str, target: str) -> Dict:
    """
    获取文件内容.

    返回示例:
    {
      "status": 200,
      "data": "eula=false\n", // 文件内容
      "time": 1718594177859
    }
    """


@api('PUT', 'api/files/', query_keys=['daemonId', 'uuid'])
def update_file(daemonId: str, uuid: str, target: str, text: str) -> Dict:
    """
    更新文件内容.

    返回示例:
    {
      "status": 200,
      "data": true,
      "time": 1718594177859
    }
    """


@api('POST', 'api/files/download', query_keys=['file_name', 'daemonId', 'uuid'])
def get_download_config(file_name: str, daemonId: str, uuid: str) -> Dict:
    """
    获取下载配置.

    返回示例:
    {
      "status": 200,
      "data": true,
      "time": 1718594177859
    }
    """


@api('POST', 'api/files/upload', query_keys=['upload_dir', 'daemonId', 'uuid'])
def get_upload_config(upload_dir: str, daemonId: str, uuid: str) -> Dict:
    """
    获取上传配置.

    返回示例:
    {
      "status": 200,
      "data": true,
      "time": 1718594177859
    }
    """


@api('POST', 'api/files/copy', query_keys=['daemonId', 'uuid'])
def copy_files(daemonId: str, uuid: str, targets: List[List[str]]) -> Dict:
    """
    复制文件.

    返回示例:
    {
      "status": 200,
      "data": true,
      "time": 1718594177859
    }
    """


@api('PUT', 'api/files/move', query_keys=['daemonId', 'uuid'])
def move_files(daemonId: str, uuid: str, targets: List[List[str]]) -> Dict:
    """
    移动或重命名.

    返回示例:
    {
      "status": 200,
      "data": true,
      "time": 1718594177859
    }
    """


@api('POST', 'api/files/compress', query_keys=['daemonId', 'uuid'])
def compress_files(daemonId: str, uuid: str, source: str, targets: List[str], code: str = 'utf-8', type: int = 1) -> Dict:
    """
    压缩文件.

    返回示例:
    {
      "status": 200,
      "data": true,
      "time": 1718594177859
    }
    """


@api('POST', 'api/files/compress', query_keys=['daemonId', 'uuid'])
def extract_files(daemonId: str, uuid: str, source: str, targets: str, code: str = 'utf-8', type: int = 2) -> Dict:
    """
    解压文件.

    返回示例:
    {
      "status": 200,
      "data": true,
      "time": 1718594177859
    }
    """


@api('DELETE', 'api/files', query_keys=['daemonId', 'uuid'])
def delete_files(daemonId: str, uuid: str, targets: List[str]) -> Dict:
    """
    删除文件.

    返回示例:
    {
      "status": 200,
      "data": true,
      "time": 1718594177859
    }
    """


@api('POST', 'api/files/touch', query_keys=['daemonId', 'uuid'])
def touch_file(daemonId: str, uuid: str, target: str) -> Dict:
    """
    新建文件.

    返回示例:
    {
      "status": 200,
      "data": true,
      "time": 1718594177859
    }
    """


@api('POST', 'api/files/mkdir', query_keys=['daemonId', 'uuid'])
def mkdir(daemonId: str, uuid: str, target: str) -> Dict:
    """
    新建文件夹.

    返回示例:
    {
      "status": 200,
      "data": true,
      "time": 1718594177859
    }
    """

