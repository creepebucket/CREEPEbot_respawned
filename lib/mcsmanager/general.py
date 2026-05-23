from typing import Dict

from lib.mcsmanager import api


@api('GET', 'api/service/remote_services_system')
def get_remote_node_list() -> Dict:
    """
    获取远程节点列表.

    返回示例:
    {
      // 状态参数
      // 200：正常，返回相应内容
      // 400：请求参数不正确
      // 403：权限不足
      // 500：程序错误
      "status": 200,
      // 响应节点列表
      "data": [
        {
          "version": "3.9.0",
          "process": {
            "cpu": 5625000 //CPU 使用
            "memory": 132437320, // 内存使用
            "cwd": "D:\\Workspace\\MCSM\\MCSManager-Daemon" //守护进程 目录
          },
          "instance": {
            "running": 1, // 运行的实例
            "total": 6 // 总共实例
          },
          "system": {
            "type": "Windows_NT", //系统类型
            "hostname": "MyComputer", //系统名称
            "platform": "win32", //系统平台
            "release": "11.0.22000", //版本
            "uptime": 410445, //在线时长
            "cwd": "D:\\Workspace\\MCSM\\MCSManager-Daemon", //守护进程 目录
            "loadavg": [0, 0, 0], //负载
            "freemem": 5700775936, //剩余内存
            "cpuUsage": 0.0490009222256379, //CPU使用
            "memUsage": 0.6651475749266619, //内存使用
            "totalmem": 17024741376, //总内存
            "processCpu": 0,
            "processMem": 0
          }
        }
      ],
      // 请求完成处理的时间可用于测量延迟。
      "time": 1643879914006
    }
    """

@api('GET', 'api/overview')
def get_overview() -> Dict:
    """
    获取 MCSManager 概览.

    返回示例:
    {
      "status": 200,
      "data": {
        "version": "10.2.1",
        "specifiedDaemonVersion": "4.4.1",
        "process": {
          "cpu": 0,
          "memory": 219439104, // Panel Memory Usage
          "cwd": "Z:\\Workspace\\MCSManager\\panel"
        },
        "record": {
          "logined": 2,
          "illegalAccess": 2,
          "banips": 0,
          "loginFailed": 0
        },
        "system": {
          "user": {
            "uid": -1,
            "gid": -1,
            "username": "MCSManager",
            "homedir": "X:\\Users\\MCSManager",
            "shell": null
          },
          // 面板上的内存使用情况
          "time": 1718594177859,
          "totalmem": 16577519520,
          "freemem": 10966386688,
          "type": "Windows_NT",
          "version": "Windows 10 Pro for Workstations",
          "node": "v17.9.1",
          "hostname": "MCSManager-Workstation",

          // 仅限 Linux
          "loadavg": [0, 0, 0],

          "platform": "win32",
          "release": "10.0.22631",
          "uptime": 905020.0,
          "cpu": 0.11684482123110951
        },

        // 面板上的内存和 CPU 使用情况（统计图）
        "chart": {
          "system": [
            {
              "cpu": 8.1,
              "mem": 64.5
            }
          ],
          "request": [
            {
              "value": 6,
              "totalInstance": 23,
              "runningInstance": 3
            }
          ]
        },
        "remoteCount": {
          "available": 3,
          "total": 3
        },

        // Daemon List
        "remote": [
          {
            "version": "3.4.0",
            "process": {
              "cpu": 3550442695,
              "memory": 22620272,
              "cwd": "/opt/mcsmanager/daemon"
            },
            "instance": {
              "running": 0,
              "total": 6
            },

            // Daemon 上的 CPU 和内存使用情况。
            "system": {
              "type": "Linux",
              "hostname": "NYA-Dev-01",
              "platform": "linux",
              "release": "5.15.0-101-generic",
              "uptime": 39.63,
              "cwd": "/opt/mcsmanager/daemon",
              "loadavg": [3.5, 0.85, 0.28],
              "freemem": 7254478848,
              "cpuUsage": 0.002512562814070307,
              "memUsage": 0.12453628345617548,
              "totalmem": 8286441472,
              "processCpu": 0,
              "processMem": 0
            },

            // 节点上的CPU和内存使用情况（图表）.
            "cpuMemChart": [
              {
                "cpu": 0,
                "mem": 13
              }
            ],

            // 节点 UUID
            "uuid": "957c6bddf379445c82bac5edf7684bbc",
            "ip": "s1.example.com",
            "port": 24444,
            "prefix": "",
            "available": true,
            "remarks": "CN-ZJ-DEV-01"
          }
        ]
      },
      "time": 1718594177859
    }
    """