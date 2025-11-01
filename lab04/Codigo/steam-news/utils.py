import pandas as pd
from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION

def count_news_per_date():
    client = MongoClient(MONGO_URI)
    collection = client[MONGO_DB][MONGO_COLLECTION]

    cursor = collection.find({"timestamp_created": {"$exists": True}})
    news = list(cursor)

    if not news:
        print("Nenhuma review com timestamp encontrada.")
        return

    df = pd.DataFrame(news)
    df["timestamp_created"] = pd.to_datetime(df["timestamp_created"], unit='s')
    df["date"] = df["timestamp_created"].dt.date
    review_counts = df.groupby("date").size()

    print("\nQuantidade de news por data:")
    print(review_counts)