import re
from typing import Dict, Optional, Any, List

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

mongo_client: MongoClient = None
database: Database = None

config_collection: Collection = None

def connect_database(connection: str):
    global mongo_client, database, config_collection
    mongo_client = MongoClient(connection)
    database = mongo_client['rules']

    # 加载各集合
    config_collection = database['config']


# 配置管理工具

def get(name: str) -> Optional[Dict[str, Any]]:
    if config_collection is None:
        return None
    doc = config_collection.find_one({'name': name})
    if doc is None:
        return None
    return doc

def set(name: str, key_name: str, data):
    config_collection.update_one({'name': name}, {'$set': {key_name: data}}, upsert=True)

class MongoConfig:
    """
    配置基类

    用于(群)会话信息, 用户信息等
    """

    def __init__(self, config_key):
        self.config_key = config_key

    def get(self, name: str, default=None):
        """
        查询一个配置项, 在默认值为None时没有此项会直接抛出异常, 路径用'/'分割
        :param default: 默认值
        :param name: 查询键
        :return: 结果
        """

        config = get(self.config_key)
        if config is None:
            if default is None:
                raise KeyError(f'配置 {self.config_key} 不存在')

            return default

        parts = name.split('/')
        current = config

        for i, part in enumerate(parts):

            if not isinstance(current, dict):
                raise TypeError(f'此项结果不是字典: {'/'.join(parts[:i])}')

            if part not in current:
                if default is None:
                    raise KeyError(f'路径 {name} 不存在键 {part}')
                return default

            current = current[part]

        return current

    def set(self, name: str, data) -> None:
        """
        设置一个配置, 没有此项会自动创建, 支持'/'分割的路径系统
        :param name: 查询键，例如 'a/b/c'
        :param data: 数据
        """
        # 将用户友好的 '/' 路径转为 MongoDB 的 '.' 嵌套字段路径
        key_path = name.replace('/', '.')
        set(self.config_key, key_path, data)

class PersonalConfig(MongoConfig):
    """
    用户信息
    """

    def __init__(self, name):
        super().__init__(f'local_user_{name}')

        self.name = name

    def get_tags(self) -> List:
        """
        获取所有标签
        :return: 标签
        """

        return self.get('tags', [])

    def has_tag(self, tag: str) -> bool:
        """
        检查指定标签是否存在
        :param tag: 需要检查的标签
        :return: 是否存在
        """

        return tag in self.get('tags', [])

    def add_tag(self, tag: str) -> None:
        """
        给用户添加指定标签
        :param tag: 需要添加的标签
        """

        tags = self.get_tags()
        if tag in tags:
            return

        tags.append(tag)
        self.set('tags', tags)

    def del_tag(self, tag: str) -> None:
        """
        删除指定标签 (没有标签没有反应)
        :param tag: 需要删除的标签
        """

        tags = self.get_tags()
        if tag not in tags:
            return

        tags.remove(tag)
        self.set('tags', tags)

    def get_role(self) -> str:
        """
        获取全局权限等级 (SUPER_ADMIN/USER/ADMIN)
        :return: 等级
        """

        if self.name in toml_config_dict['general']['superusers']:
            return 'SUPER_ADMIN'

        return self.get('role', 'USER')

    def set_role(self, role: str) -> None:
        """
        设置全局权限等级
        :param role: 等级
        """

        self.set('role', role)


class GlobalConfig(MongoConfig):
    """
    全局配置
    """
    def __init__(self):
        super().__init__('global')

global_config = GlobalConfig()

toml_config_dict = {}

def set_toml_config(c):
    global  toml_config_dict
    toml_config_dict = c
