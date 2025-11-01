import os
import logging
from pymongo import MongoClient
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

MONGO_URI = "mongodb+srv://andradelucasmo:Q0I9Yp9Ai6mWK1vI@cluster0.5kddnrk.mongodb.net/"
MONGO_DB = "games"

BASE_DIR = os.path.dirname(__file__)
ANALISE_CRUZADA_DIR = os.path.join(BASE_DIR, "analise_cruzada")
GRAFICOS_DIR = os.path.join(ANALISE_CRUZADA_DIR, "graficos")
os.makedirs(GRAFICOS_DIR, exist_ok=True)
log_path = os.path.join(ANALISE_CRUZADA_DIR, "log_classificacao_release.log")

logging.basicConfig(
    filename=log_path,
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_lda_results_from_mongodb():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db["lda_patchnotes"]
    resultados = list(collection.find({}))
    client.close()
    return resultados

def get_sentiment_data_from_mongodb():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db["releases_classificadas_json"]
    resultados = list(collection.find({}))
    client.close()
    return resultados

def analyze_cross_data():
    try:
        lda_results = get_lda_results_from_mongodb()
        sentiment_data = get_sentiment_data_from_mongodb()
        
        if not lda_results or not sentiment_data:
            logging.warning("Dados insuficientes para análise cruzada.")
            return

        for genero_data in sentiment_data:
            genero = genero_data["genero"]
            lda_result = next((item for item in lda_results if item["genero"] == genero), None)
            if not lda_result:
                continue

            topico_stats = {}

            for grupo in ["releases_positivas", "releases_negativas"]:
                if grupo not in genero_data or grupo not in lda_result:
                    continue

                releases = genero_data[grupo]
                distribuicoes = lda_result[grupo].get("distribuicoes", {})
                coerencia = lda_result[grupo].get("coerencia", 0.0)

                for idx, release in enumerate(releases):
                    if "avg_sentiment" not in release:
                        continue

                    chave = f"release_{idx}"
                    topic_dist = distribuicoes.get(chave)
                    if not topic_dist:
                        continue
                    
                    topico_dominante = max(topic_dist, key=lambda x: x[1])[0]
                    topico_key = str(topico_dominante)

                    if topico_key not in topico_stats:
                        topico_stats[topico_key] = {
                            "sentimentos": [],
                            "coerencia": coerencia,
                            "grupo": grupo
                        }

                    topico_stats[topico_key]["sentimentos"].append(release["avg_sentiment"])

            topicos_identificadores = []
            medias_sentimento = []
            coerencia_list = []

            for topico, data in topico_stats.items():
                if data["sentimentos"]:
                    identificador = f"{genero} {'Positivo' if data['grupo'] == 'releases_positivas' else 'Negativo'} {topico}"
                    topicos_identificadores.append(identificador)
                    medias_sentimento.append(sum(data["sentimentos"]) / len(data["sentimentos"]))
                    coerencia_list.append(data["coerencia"])

            if not topicos_identificadores:
                continue

            # Gráfico 2: Coerência vs. Sentimento
            plt.figure(figsize=(10, 6))
            plt.scatter(
                medias_sentimento,
                coerencia_list,
                c=['green' if x > 0 else 'red' for x in medias_sentimento],
                s=100
            )
            for i, (x, y) in enumerate(zip(medias_sentimento, coerencia_list)):
                plt.annotate(
                    topicos_identificadores[i],
                    (x, y),
                    textcoords="offset points",
                    xytext=(0, 5),
                    ha='center',
                    fontsize=8
                )
            plt.title(f"Coerência vs. Sentimento - {genero}")
            plt.xlabel("Média de Sentimento")
            plt.ylabel("Coerência do Tópico")
            plt.grid(True)
            plt.savefig(os.path.join(GRAFICOS_DIR, f"coerencia_vs_sentimento_{genero}.png"), bbox_inches='tight')
            plt.close()

    except Exception as e:
        logging.error(f"Erro na análise cruzada: {str(e)}")


if __name__ == "__main__":
    logging.info("Iniciando análise cruzada...")
    analyze_cross_data()
    logging.info("Análise cruzada concluída.")