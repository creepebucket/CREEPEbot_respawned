from typing import Dict

from lib.database import config_collection


# 配置管理工具

def get(name: str) -> Dict:
    return config_collection.find_one({'name': name})['data']

def set(name: str, data: Dict):
    config_collection.update_one({'name': name}, {'$set': {'data': data}})

def add(name: str, data: Dict):
    config_collection.insert_one({'name': name, 'data': data})