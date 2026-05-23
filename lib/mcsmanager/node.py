from typing import Dict

from lib.mcsmanager import api


@api('POST', 'api/service/remote_service')
def add_node(ip: str, port: int, apiKey: str, prefix: str = '', remarks: str = '') -> Dict:
    """
    添加节点.

    返回示例:
    {
      "status": 200,
      "data": "499e1012a21443278a7ec63a3a95860b", // 新增节点的节点 ID
      "time": 1718594177859
    }
    """


@api('DELETE', 'api/service/remote_service', query_keys=['uuid'])
def delete_node(uuid: str) -> Dict:
    """
    删除节点.

    返回示例:
    {
      "status": 200,
      "data": true,
      "time": 1718594177859
    }
    """


@api('GET', 'api/service/link_remote_service')
def link_node(uuid: str) -> Dict:
    """
    连接节点.

    返回示例:
    {
      "status": 200,
      "data": true,
      "time": 1718594177859
    }
    """


@api('PUT', 'api/service/remote_service', query_keys=['uuid'])
def update_node(uuid: str, ip: str, port: int, prefix: str = '', available: bool = False, remarks: str = '', apiKey: str = '') -> Dict:
    """
    更新节点连接参数.

    返回示例:
    {
      "status": 200,
      "data": true,
      "time": 1718594177859
    }
    """
