from steam_api import get_steam_reviews
from mongo_client import get_mongo_collection, insert_reviews, clear_collection
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION
from collections import defaultdict
import time

def main():
    # A collection onde estão os gêneros com jogos
    info_collection = get_mongo_collection(MONGO_URI, MONGO_DB, "top_sellers_info")
    jogos_collection = get_mongo_collection(MONGO_URI, MONGO_DB, MONGO_COLLECTION)
    
    clear_collection(jogos_collection)

    total_reviews = jogos_collection.count_documents({})
    print(f"\nTotal de reviews na collection '{MONGO_COLLECTION}': {total_reviews}")

    # Obter todos os documentos da collection
    generos = list(info_collection.find({}))
    if not generos:
        print("Nenhum gênero encontrado em 'top_sellers_info'")
        return

    resumo_reviews = defaultdict(int)

    # Iterar sobre todos os jogos de todos os gêneros
    for genero_doc in generos:
        jogos = genero_doc.get("jogos", [])
        for jogo in jogos:
            appid = jogo.get("appid")
            nome = jogo.get("nome")

            if not appid or not nome:
                continue

            print(f"\n🔍 Buscando reviews para: {nome} (appid: {appid})...")
            reviews = get_steam_reviews(appid, total_reviews=5000)

            # Adiciona o appid e nome a cada review
            for r in reviews:
                r["appid"] = appid
                r["nome"] = nome

            insert_reviews(jogos_collection, reviews)

            resumo_reviews[f"{appid} - {nome}"] += len(reviews)

            time.sleep(3)

    # Resumo final
    print("\nResumo de reviews coletadas:")
    for chave, total in resumo_reviews.items():
        print(f"🎮 {chave}: {total} reviews")

    total_reviews = jogos_collection.count_documents({})
    print(f"\nTotal de reviews na collection '{MONGO_COLLECTION}': {total_reviews}")

    print("\nColeta e inserção concluídas com sucesso.")

if __name__ == "__main__":
    main()