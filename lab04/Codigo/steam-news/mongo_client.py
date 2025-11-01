from pymongo import MongoClient

def get_mongo_collection(uri, db_name, collection_name):
    client = MongoClient(uri)
    db = client[db_name]
    return db[collection_name]

def insert_news(collection, news):
    if news:
        collection.insert_many(news)

def clear_collection(collection):
    collection.delete_many({})
    print(f"Collection '{collection.name}' limpa com sucesso.")