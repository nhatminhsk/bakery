from pymongo import MongoClient


def MongoDB(uri: str,db_name: str, collection_name: str):
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]

    return collection