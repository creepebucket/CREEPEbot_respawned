from typing import Dict, Optional, List, Any

from lib.mcsmanager import api


@api('GET', 'api/service/remote_service_instances')
def get_instance_list(daemonId: str, status: str, page: int = 1, page_size: int = 10, instance_name: Optional[str] = None) -> Dict:
    """
    实例列表.

    返回示例:
    {
      "status": 200,
      "data": {
        "maxPage": 1,
        "pageSize": 10,
        "data": InstanceDetail[]
      },
      "time": 1718594177859
    }

    实例详细信息:
    {
      "config": InstanceConfig,
      "info": {
        "currentPlayers": -1,
        "fileLock": 0,
        "maxPlayers": -1,
        "openFrpStatus": false,
        "playersChart": [],
        "version": "",
      },
      "instanceUuid": "50c73059001b436fa85c0d8221c157cf",
      "processInfo": {
        "cpu": 0,
        "memory": 0,
        "ppid": 0,
        "pid": 0,
        "ctime": 0,
        "elapsed": 0,
        "timestamp": 0
      },
      "space": 0,
      "started": 6, // 启动次数
      "status": 3,  // -1 = 忙碌,
                    // 0  = 停止,
                    // 1  = 停止中,
                    // 2  = 启动中,
                    // 3  = 运行中
    }

    实例配置:
    {
      "nickname": "New Name",             // 实例名称
      "startCommand": "cmd.exe",          // 启动命令
      "stopCommand":  "^C",               // 停止命令
      "cwd": "/workspaces/my_server/",    // 运行目录(主机)
      "ie": "gbk",                        // 输入 encode
      "oe": "gbk",                        // 输出 encode
      "createDatetime": 1709631756708,    // 创建时间
      "lastDatetime": 1709631756708,      // 最后启动时间
      "type": "universal",                // 实例类型
      "tag": [],                          // 实例标签
      "endTime": 1709631756708,           // 到期时间
      "fileCode": "gbk",                  // 文件编码
      "processType": "docker",            // 进程类型
      "updateCommand": "shutdown -s",     // 更新命令
      "actionCommandList": [],
      "crlf": 2,
      "docker": DockerConfig,

      // Steam RCON
      "enableRcon": true,
      "rconPassword": "123456",
      "rconPort": 2557,
      "rconIp": "192.168.1.233",

      // 终端选项
      "terminalOption": {
        "haveColor": false,
        "pty": true,
      },
      "eventTask": {
        "autoStart": false,
        "autoRestart": true,
        "ignore": false,
      },
      "pingConfig": {
        "ip": "",
        "port": 25565,
        "type": 1,
      }
    }
    """


@api('GET', 'api/instance')
def get_instance_detail(uuid: str, daemonId: str) -> Dict:
    """
    实例详情.

    返回示例:
    {
      "status": 200,
      "data": InstanceDetail,
      "time": 1718594177859
    }

    实例详细信息:
    {
      "config": InstanceConfig,
      "info": {
        "currentPlayers": -1,
        "fileLock": 0,
        "maxPlayers": -1,
        "openFrpStatus": false,
        "playersChart": [],
        "version": "",
      },
      "instanceUuid": "50c73059001b436fa85c0d8221c157cf",
      "processInfo": {
        "cpu": 0,
        "memory": 0,
        "ppid": 0,
        "pid": 0,
        "ctime": 0,
        "elapsed": 0,
        "timestamp": 0
      },
      "space": 0,
      "started": 6, // 启动次数
      "status": 3,  // -1 = 忙碌,
                    // 0  = 停止,
                    // 1  = 停止中,
                    // 2  = 启动中,
                    // 3  = 运行中
    }

    实例配置:
    {
      "nickname": "New Name",             // 实例名称
      "startCommand": "cmd.exe",          // 启动命令
      "stopCommand":  "^C",               // 停止命令
      "cwd": "/workspaces/my_server/",    // 运行目录(主机)
      "ie": "gbk",                        // 输入 encode
      "oe": "gbk",                        // 输出 encode
      "createDatetime": 1709631756708,    // 创建时间
      "lastDatetime": 1709631756708,      // 最后启动时间
      "type": "universal",                // 实例类型
      "tag": [],                          // 实例标签
      "endTime": 1709631756708,           // 到期时间
      "fileCode": "gbk",                  // 文件编码
      "processType": "docker",            // 进程类型
      "updateCommand": "shutdown -s",     // 更新命令
      "actionCommandList": [],
      "crlf": 2,
      "docker": DockerConfig,

      // Steam RCON
      "enableRcon": true,
      "rconPassword": "123456",
      "rconPort": 2557,
      "rconIp": "192.168.1.233",

      // 终端选项
      "terminalOption": {
        "haveColor": false,
        "pty": true,
      },
      "eventTask": {
        "autoStart": false,
        "autoRestart": true,
        "ignore": false,
      },
      "pingConfig": {
        "ip": "",
        "port": 25565,
        "type": 1,
      }
    }
    """


@api('POST', 'api/instance', query_keys=['daemonId'])
def create_instance(daemonId: str, config: Dict[str, Any]) -> Dict:
    """
    创建实例.

    返回示例:
    {
      "status": 200,
      "data": {
        "instanceUuid": "50c73059001b436fa85c0d8221c157cf",
        "config": InstanceConfig
      },
      "time": 1718594177859
    }

    实例配置:
    {
      "nickname": "New Name",             // 实例名称
      "startCommand": "cmd.exe",          // 启动命令
      "stopCommand":  "^C",               // 停止命令
      "cwd": "/workspaces/my_server/",    // 运行目录(主机)
      "ie": "gbk",                        // 输入 encode
      "oe": "gbk",                        // 输出 encode
      "createDatetime": 1709631756708,    // 创建时间
      "lastDatetime": 1709631756708,      // 最后启动时间
      "type": "universal",                // 实例类型
      "tag": [],                          // 实例标签
      "endTime": 1709631756708,           // 到期时间
      "fileCode": "gbk",                  // 文件编码
      "processType": "docker",            // 进程类型
      "updateCommand": "shutdown -s",     // 更新命令
      "actionCommandList": [],
      "crlf": 2,
      "docker": DockerConfig,

      // Steam RCON
      "enableRcon": true,
      "rconPassword": "123456",
      "rconPort": 2557,
      "rconIp": "192.168.1.233",

      // 终端选项
      "terminalOption": {
        "haveColor": false,
        "pty": true,
      },
      "eventTask": {
        "autoStart": false,
        "autoRestart": true,
        "ignore": false,
      },
      "pingConfig": {
        "ip": "",
        "port": 25565,
        "type": 1,
      }
    }
    """


@api('PUT', 'api/instance', query_keys=['uuid', 'daemonId'])
def update_instance(uuid: str, daemonId: str, config: Dict[str, Any]) -> Dict:
    """
    更新实例配置.

    返回示例:
    {
      "status": 200,
      "data": {
        "instanceUuid": "50c73059001b436fa85c0d8221c157cf"
      },
      "time": 1718594177859
    }
    """


@api('DELETE', 'api/instance', query_keys=['daemonId'])
def delete_instance(daemonId: str, uuids: List[str], deleteFile: bool = False) -> Dict:
    """
    删除实例.

    返回示例:
    {
      "status": 200,
      "data": [
        "50c73059001b436fa85c0d8221c157cf",
        "11c2f4c89b9e4e1da819dc56bf16f151"
      ], // Instance Id
      "time": 1718594177859
    }
    """


@api('GET', 'api/protected_instance/open')
def start_instance(uuid: str, daemonId: str) -> Dict:
    """
    启动实例.

    返回示例:
    {
      "status": 200,
      "data": {
        "instanceUuid": "50c73059001b436fa85c0d8221c157cf"
      },
      "time": 1718594177859
    }
    """


@api('GET', 'api/protected_instance/stop')
def stop_instance(uuid: str, daemonId: str) -> Dict:
    """
    停止实例.

    返回示例:
    {
      "status": 200,
      "data": {
        "instanceUuid": "50c73059001b436fa85c0d8221c157cf"
      },
      "time": 1718594177859
    }
    """


@api('GET', 'api/protected_instance/restart')
def restart_instance(uuid: str, daemonId: str) -> Dict:
    """
    重启实例.

    返回示例:
    {
      "status": 200,
      "data": {
        "instanceUuid": "50c73059001b436fa85c0d8221c157cf"
      },
      "time": 1718594177859
    }
    """


@api('GET', 'api/protected_instance/kill')
def kill_instance(uuid: str, daemonId: str) -> Dict:
    """
    强制结束实例进程.

    返回示例:
    {
      "status": 200,
      "data": {
        "instanceUuid": "50c73059001b436fa85c0d8221c157cf"
      },
      "time": 1718594177859
    }
    """


@api('POST', 'api/instance/multi_start')
def multi_start(body: List[Dict[str, str]]) -> Dict:
    """
    批量启动.
    body: [{"instanceUuid": "...", "daemonId": "..."}, ...]

    返回示例:
    {
      "status": 200,
      "data": true,
      "time": 1718594177859
    }
    """


@api('POST', 'api/instance/multi_stop')
def multi_stop(body: List[Dict[str, str]]) -> Dict:
    """
    批量停止.
    body: [{"instanceUuid": "...", "daemonId": "..."}, ...]

    返回示例:
    {
      "status": 200,
      "data": true,
      "time": 1718594177859
    }
    """


@api('POST', 'api/instance/multi_restart')
def multi_restart(body: List[Dict[str, str]]) -> Dict:
    """
    批量重启.
    body: [{"instanceUuid": "...", "daemonId": "..."}, ...]

    返回示例:
    {
      "status": 200,
      "data": true,
      "time": 1718594177859
    }
    """


@api('POST', 'api/instance/multi_kill')
def multi_kill(body: List[Dict[str, str]]) -> Dict:
    """
    批量强杀.
    body: [{"instanceUuid": "...", "daemonId": "..."}, ...]

    返回示例:
    {
      "status": 200,
      "data": true,
      "time": 1718594177859
    }
    """


@api('POST', 'api/protected_instance/asynchronous', query_keys=['uuid', 'daemonId', 'task_name'])
def update_instance_task(uuid: str, daemonId: str, task_name: str = 'update') -> Dict:
    """
    更新实例.

    返回示例:
    {
      "status": 200,
      "data": true,
      "time": 1718594177859
    }
    """


@api('GET', 'api/protected_instance/command')
def send_command(uuid: str, daemonId: str, command: str) -> Dict:
    """
    发送命令.

    返回示例:
    {
      "status": 200,
      "data": {
        "instanceUuid": "50c73059001b436fa85c0d8221c157cf"
      },
      "time": 1718594177859
    }
    """


@api('GET', 'api/protected_instance/outputlog')
def get_output_log(uuid: str, daemonId: str, size: Optional[int] = None) -> Dict:
    """
    获取输出.

    返回示例:
    {
      "status": 200,
      "data": "[INFO]: Done (12.138s)! For help, type \"help\"\n",
      "time": 1718594177859
    }
    """


@api('POST', 'api/protected_instance/install_instance', query_keys=['daemonId', 'uuid'])
def reinstall_instance(daemonId: str, uuid: str, targetUrl: str, title: str, description: str = '') -> Dict:
    """
    重新安装.

    返回示例:
    {
      "status": 200,
      "data": true,
      "time": 1718594177859
    }
    """
