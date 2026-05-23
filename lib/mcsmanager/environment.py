from typing import Dict

from lib.mcsmanager import api


@api('GET', 'api/environment/image')
def get_image_list(daemonId: str) -> Dict:
    """
    获取镜像列表.

    返回示例:
    {
      "status": 200,
      "data": DockerImageList,
      "time": 1718594177859
    }
    """


@api('GET', 'api/environment/containers')
def get_container_list(daemonId: str) -> Dict:
    """
    获取容器列表.

    返回示例:
    {
      "status": 200,
      "data": DockerContainerList,
      "time": 1718594177859
    }
    """


@api('GET', 'api/environment/network')
def get_network_list(daemonId: str) -> Dict:
    """
    获取网络接口列表.

    返回示例:
    {
      "status": 200,
      "data": DockerNetworkList,
      "time": 1718594177859
    }
    """


@api('POST', 'api/environment/image', query_keys=['daemonId'])
def create_image(daemonId: str, dockerFile: str, name: str, tag: str = 'latest') -> Dict:
    """
    新增镜像.

    返回示例:
    {
      "status": 200,
      "data": true,
      "time": 1718594177859
    }
    """


@api('GET', 'api/environment/progress')
def get_build_progress(daemonId: str) -> Dict:
    """
    构建进度.

    返回示例:
    {
      "status": 200,
      "data": {
        "mcsm-custom:latest": -1 // -1 = Failed, 1 = Building, 2 = Complete
        // ...more...
      },
      "time": 1718594177859
    }
    """

