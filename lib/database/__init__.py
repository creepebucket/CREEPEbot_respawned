from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

# 数据库连接工具

mongo_client: MongoClient = None
database: Database = None

config_collection: Collection = None

def connect_database(connection: str):
    global mongo_client, database, config_collection
    mongo_client = MongoClient(connection)
    database = mongo_client['creepebot_respawned']

    # 加载各集合
    config_collection = database['config']
