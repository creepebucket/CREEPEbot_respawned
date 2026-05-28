from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

# 数据库连接工具

mongo_client: MongoClient = None
database: Database = None

config_collection: Collection = None
backup_collection: Collection = None

def connect_database(connection: str):
    global mongo_client, database, config_collection, backup_collection
    mongo_client = MongoClient(connection)
    database = mongo_client['rules']

    # 加载各集合
    config_collection = database['config']
    backup_collection = database['backup']
    from lib.backup import auto
    from lib import backup
    backup.backup_collection = auto.backup_collection = backup_collection
