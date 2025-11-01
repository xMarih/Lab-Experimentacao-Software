import pandas as pd
from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION

def count_reviews_per_date():
    client = MongoClient(MONGO_URI)
    collection = client[MONGO_DB][MONGO_COLLECTION]

    cursor = collection.find({"timestamp_created": {"$exists": True}})
    reviews = list(cursor)

    if not reviews:
        print("Nenhuma review com timestamp encontrada.")
        return

    df = pd.DataFrame(reviews)
    df["timestamp_created"] = pd.to_datetime(df["timestamp_created"], unit='s')
    df["date"] = df["timestamp_created"].dt.date
    review_counts = df.groupby("date").size()

    print("\nQuantidade de reviews por data:")
    print(review_counts)