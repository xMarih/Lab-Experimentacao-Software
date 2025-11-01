from steam_news_api import get_steam_news
from mongo_client import get_mongo_collection, insert_news, clear_collection
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION
from collections import defaultdict
import time

def main():
    # A collection onde estão os gêneros com jogos
    info_collection = get_mongo_collection(MONGO_URI, MONGO_DB, "top_sellers_info")
    jogos_collection = get_mongo_collection(MONGO_URI, MONGO_DB, MONGO_COLLECTION)
    
    clear_collection(jogos_collection)

    total_news = jogos_collection.count_documents({})
    print(f"\nTotal de news na collection '{MONGO_COLLECTION}': {total_news}")

    # Obter todos os documentos da collection
    generos = list(info_collection.find({}))
    if not generos:
        print("Nenhum gênero encontrado em 'top_sellers_info'")
        return

    resumo_news = defaultdict(int)

    # Iterar sobre todos os jogos de todos os gêneros
    for genero_doc in generos:
        jogos = genero_doc.get("jogos", [])
        for jogo in jogos:
            appid = jogo.get("appid")
            nome = jogo.get("nome")

            if not appid or not nome:
                continue

            print(f"\nBuscando news para: {nome} (appid: {appid})...")
            news = get_steam_news(appid, total_news=5000)

            # Adiciona o appid e nome a cada new
            for r in news:
                r["appid"] = appid
                r["nome"] = nome

            insert_news(jogos_collection, news)

            resumo_news[f"{appid} - {nome}"] += len(news)

            time.sleep(3)

    # Resumo final
    print("\nResumo de news coletadas:")
    for chave, total in resumo_news.items():
        print(f"🎮 {chave}: {total} news")

    total_news = jogos_collection.count_documents({})
    print(f"\nTotal de news na collection '{MONGO_COLLECTION}': {total_news}")

    print("\nColeta e inserção concluídas com sucesso.")

if __name__ == "__main__":
    main()