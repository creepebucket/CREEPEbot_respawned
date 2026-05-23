import requests
from functools import wraps
import re
from urllib.parse import urljoin
import inspect

from lib import logger

API_KEY = None
BASE_URL = None

def set_api_key(key: str):
    global API_KEY
    API_KEY = key

def set_base_url(url: str):
    global BASE_URL
    BASE_URL = url

def path_format_params(path: str):
    """提取路径中的格式化参数名，例如 '/users/{user_id}' -> ['user_id']"""
    return re.findall(r'\{(\w+)\}', path)

def api(method: str, path: str, query_keys=None):
    """
    装饰器：将函数调用转换为 API 请求。
    自动将全局常量 API_KEY 作为查询参数 ?api_key=... 添加到请求中。
    """
    def decorator(func):
        @wraps(func)
        def wrapper(**kwargs):
            bound = inspect.signature(func).bind_partial(**kwargs)
            bound.apply_defaults()
            kwargs = bound.arguments

            # 0. 检查APIKEY/BASEURL是否存在
            if API_KEY is None:
                logger.crit('收到MCSM管理请求, 但是**未设置** API KEY! 请检查 `config.toml`是否设置?')
                return None
            if BASE_URL is None:
                logger.crit('收到MCSM管理请求, 但是**未设置** BASE URL! 请检查 `config.toml`是否设置?')
                return None

            # 1. 构造 URL：用参数替换路径中的占位符
            url = urljoin(str(BASE_URL).rstrip('/') + '/', str(path).lstrip('/')).format(**kwargs)

            # 2. 分离路径参数与请求参数（路径参数已用于 URL 构造，剩余的都是请求参数）
            path_params = path_format_params(path)
            request_params = {k: v for k, v in kwargs.items() if k not in path_params}
            request_params = {k: v for k, v in request_params.items() if v is not None}

            # 3. 基础查询参数：始终携带 API Key
            query_params = {'apikey': API_KEY}
            headers = {'x-requested-with': 'xmlhttprequest'}

            # 4. 根据 HTTP 方法构建请求
            if method.upper() == 'GET':
                # GET：所有请求参数都作为查询参数
                query_params.update(request_params)
                resp = requests.get(url, params=query_params, headers=headers)
            else:
                # POST / PUT / DELETE 等：API Key 留在查询参数中，请求参数作为 JSON body
                # 如果需要也可将部分参数作为查询参数，这里保持简洁
                query_params.update({k: request_params.pop(k) for k in (query_keys or ()) if k in request_params})

                if 'body' in request_params and len(request_params) == 1:
                    request_body = request_params['body']
                else:
                    request_body = request_params

                resp = requests.request(
                    method.upper(),
                    url,
                    params=query_params,   # API Key 在 URL 参数中
                    json=request_body,     # 其余参数放在请求体
                    headers=headers
                )

            resp.raise_for_status()
            return resp.json()

        return wrapper
    return decorator


from .general import get_remote_node_list, get_overview
from .auth import get_user_list, create_user, update_user, delete_user
from .instance import get_instance_list, get_instance_detail, create_instance, update_instance, delete_instance
from .instance import start_instance, stop_instance, restart_instance, kill_instance
from .instance import multi_start, multi_stop, multi_restart, multi_kill
from .instance import update_instance_task, send_command, get_output_log, reinstall_instance
from .node import add_node, delete_node, link_node, update_node
from .files import get_file_list, get_file_content, update_file, get_download_config, get_upload_config
from .files import copy_files, move_files, compress_files, extract_files, delete_files, touch_file, mkdir
from .environment import get_image_list, get_container_list, get_network_list, create_image, get_build_progress
