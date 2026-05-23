from typing import Optional, Dict, Any, List

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

mongo_client: MongoClient = None
database: Database = None

cache_collection: Collection = None


def connect_database(connection: str):
    global mongo_client, database, cache_collection
    mongo_client = MongoClient(connection)
    database = mongo_client['creepebot_respawned']

    cache_collection = database['cache']


def get(name: str) -> Optional[Dict[str, Any]]:
    if cache_collection is None:
        return None
    doc = cache_collection.find_one({'name': name})
    if doc is None:
        return None
    return doc


def set(name: str, data: List[Dict[str, Any]]):
    cache_collection.update_one({'name': name}, {'$set': {'data': data}}, upsert=True)


class MongoCache:
    """
    缓存基类
    """

    def __init__(self, cache_key: str):
        self.cache_key = cache_key

    def get(self) -> Optional[List[Dict[str, Any]]]:
        doc = get(self.cache_key)
        if doc is None:
            return None
        return doc['data']

    def set(self, data: List[Dict[str, Any]]) -> None:
        set(self.cache_key, data)
