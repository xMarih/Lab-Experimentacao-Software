from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION
from pymongo.errors import AutoReconnect
import time

# Função para conectar ao MongoDB e retornar a coleção
def get_mongo_collection(MONGO_URI, MONGO_DB, MONGO_COLLECTION):
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    
    # Garantir que a coleção exista
    if MONGO_COLLECTION not in db.list_collection_names():
        db.create_collection(MONGO_COLLECTION)
    
    collection = db[MONGO_COLLECTION]
    return collection

# Função para limpar a coleção
def clear_collection(collection):
    collection.delete_many({})

def insert_documents(collection, documents, batch_size=1000, retries=3):
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        for attempt in range(retries):
            try:
                collection.insert_many(batch)
                break
            except AutoReconnect as e:
                print(f"[WARN] Conexão perdida durante inserção. Tentativa {attempt + 1}/{retries}...")
                time.sleep(2)
        else:
            raise RuntimeError("Falha ao reconectar ao MongoDB após múltiplas tentativas.")

# Função para buscar reviews com mínimo de caracteres
def get_reviews_from_mongo(min_length):
    collection = get_mongo_collection(MONGO_URI, MONGO_DB, MONGO_COLLECTION)
    return list(collection.find({
        "review": {"$exists": True, "$type": "string"},
        "$expr": {"$gte": [{"$strLenCP": "$review"}, min_length]}
    }))