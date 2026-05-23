from typing import Dict, List, Optional, Any

from lib.mcsmanager import api


@api('GET', 'api/auth/search')
def get_user_list(page: int = 1, page_size: int = 20, userName: Optional[str] = None, role: Optional[str] = None) -> Dict:
    """
    获取用户列表.

    返回示例:
    {
      "status": 200,
      "data": {
        "data": [
          {
            "uuid": "********************************",
            "userName": "Admin",
            "passWord": "",
            "passWordType": 1,
            "salt": "",
            "permission": 10, // 1=用户, 10=管理员, -1=被封禁的用户
            "registerTime": 1718594128408,
            "loginTime": 1718594138590,
            // 用户拥有的实例列表
            "instances": [
              {
                "instanceUuid": "82e856fd33424e018fc2c007e1a3c4d3",
                "daemonId": "1fcdacc01eac44a7bf8fe83d34215d05"
              }
            ],
            "apiKey": "",
            "isInit": false,
            "secret": "",
            "open2FA": false
          }
        ],
        "maxPage": 1,
        "page": 1,
        "pageSize": 20,
        "total": 6
      },
      "time": 1718594177859
    }
    """


@api('POST', 'api/auth')
def create_user(username: str, password: str, permission: int = 1) -> Dict:
    """
    创建用户.

    返回示例:
    {
      "status": 200,
      "time": 1718594177859,
      "data": {
        "uuid": "046afc351bfb44a99aa5641c06e70e5a", // 新用户的 UUID
        "userName": "Admin", // 新用户的用户名
        "permission": 1 //新用户的权限
      }
    }
    """


@api('PUT', 'api/auth')
def update_user(uuid: str, config: Dict[str, Any]) -> Dict:
    """
    更新用户数据.

    返回示例:
    {
      "status":200 ,
      "data": true,
      "time": 1718594177859
    }
    """


@api('DELETE', 'api/auth')
def delete_user(body: List[str]) -> Dict:
    """
    删除用户.

    返回示例:
    {
      "status": 200,
      "data": true,
      "time": 1718594177859
    }
    """
