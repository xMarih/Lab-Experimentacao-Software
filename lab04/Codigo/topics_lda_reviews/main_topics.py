from mongo_client import get_mongo_collection, clear_collection, insert_documents
from process_review import process_reviews_with_lda
from config import MONGO_URI, MONGO_DB, TOPIC_REVIEWS_COLLECTION, LDA_TOPICS_COLLECTION

def main():
    # Obter a coleção de tópicos e reviews
    topic_reviews_collection = get_mongo_collection(MONGO_URI, MONGO_DB, TOPIC_REVIEWS_COLLECTION)
    lda_topics_collection = get_mongo_collection(MONGO_URI, MONGO_DB, LDA_TOPICS_COLLECTION)

    print("Iniciando processamento das reviews...")

    # Processar as reviews com LDA
    topics, review_data = process_reviews_with_lda()

    if topics and review_data:
        # Inserir os tópicos e reviews processados nas coleções
        insert_documents(lda_topics_collection, [{"topic_id": k, "keywords": v} for k, v in topics.items()])
        insert_documents(topic_reviews_collection, review_data)
        print("Tópicos e reviews com sentimentos salvos no MongoDB com sucesso.")
    else:
        print("Nenhum dado processado para salvar.")

if __name__ == "__main__":
    main()