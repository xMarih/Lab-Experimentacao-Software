import os
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
from tabulate import tabulate
import json
from bson import ObjectId
import logging
import matplotlib.pyplot as plt

MONGO_URI = "mongodb+srv://andradelucasmo:Q0I9Yp9Ai6mWK1vI@cluster0.5kddnrk.mongodb.net/"
MONGO_DB = "games"
DIAS_LIMITE = 365

# Diretório para logs e resultados
BASE_DIR = os.path.dirname(__file__)
RESULTADOS_DIR = os.path.join(BASE_DIR, "resultados/classificacao_release")
RESULTADOS_DIR_GRAFICOS = os.path.join(BASE_DIR, "resultados/classificacao_release/graficos_release")
os.makedirs(RESULTADOS_DIR, exist_ok=True)
os.makedirs(RESULTADOS_DIR_GRAFICOS, exist_ok=True)
log_path = os.path.join(RESULTADOS_DIR, "log_classificacao_release.log")

# Configuração do logger
logging.basicConfig(
    filename=log_path,
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def salvar_classificacao_no_mongodb(db, genero, releases_positivas, releases_negativas):
    collection = db["releases_classificadas_json"]
    documento = {
        "genero": genero,
        "releases_positivas": releases_positivas,
        "releases_negativas": releases_negativas,
        "data_processo": datetime.now(timezone.utc)
    }
    collection.insert_one(documento)
    logging.info(f"Dados salvos no MongoDB na collection 'releases_classificadas_json' para o gênero '{genero}'.")


def gerar_graficos_review_counts(df_final, genero, output_dir):
    df_final["release_date"] = pd.to_datetime(df_final["release_date"], errors="coerce")

    def plotar(df_filtrado, tipo):
        if df_filtrado.empty:
            logging.info(f"Sem dados para gerar gráfico de releases {tipo}.")
            return

        df_filtrado = df_filtrado.sort_values("release_date")
        plt.figure(figsize=(10, 5))
        plt.plot(df_filtrado["release_date"], df_filtrado["review_count_positive"], label="Reviews Positivas", marker='o')
        plt.plot(df_filtrado["release_date"], df_filtrado["review_count_negative"], label="Reviews Negativas", marker='x')
        plt.xlabel("Data da Release")
        plt.ylabel("Quantidade de Reviews")
        plt.title(f"Releases {tipo.capitalize()} - {genero}")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        filename = f"grafico_reviews_{tipo}_{genero}.png"
        path = os.path.join(output_dir, filename)
        plt.savefig(path)
        plt.close()
        logging.info(f"Gráfico salvo: {path}")

    plotar(df_final[df_final["label"] == "positive"], "positivas")
    plotar(df_final[df_final["label"] == "negative"], "negativas")

def verificar_consistencia(db, genero, appids_genero, df_final, limite_data):
    total_releases_db = db["steam_news"].count_documents({
        "appid": {"$in": appids_genero},
        "date": {"$gte": limite_data.timestamp()}
    })
    total_releases_csv = len(df_final)
    expected_intervals = total_releases_db - 1 if total_releases_db >= 2 else 0

    if total_releases_csv == expected_intervals:
        logging.info("Releases CSV e MongoDB batem.")
    else:
        logging.info(f"Diferença de releases: CSV={total_releases_csv}, MongoDB-1={expected_intervals}")

    total_reviews_db = db["topic_reviews"].count_documents({
        "appid": {"$in": appids_genero},
        "datetime_created": {"$gte": limite_data.isoformat()}
    })
    total_reviews_csv = df_final["review_count_total"].sum()

    if total_reviews_csv == total_reviews_db:
        logging.info("Reviews CSV e MongoDB batem.")
    else:
        logging.info(f"Diferença de reviews: CSV={total_reviews_csv}, MongoDB={total_reviews_db}")

def main():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    limite_data = datetime.now(timezone.utc) - timedelta(days=DIAS_LIMITE)

    jogos_df = pd.DataFrame(list(db["dados_jogos"].find({}, {"appid": 1, "genero": 1})))
    if jogos_df.empty:
        logging.info("Nenhum jogo encontrado na collection 'dados_jogos'.")
        return

    for genero, grupo_genero in jogos_df.groupby("genero"):
        appids_genero = grupo_genero["appid"].dropna().unique().tolist()
        if not appids_genero:
            continue

        logging.info(f"\nGênero: {genero}")
        logging.info(f"• Total de jogos identificados: {len(appids_genero)}")
        logging.info(f"• AppIDs: {appids_genero}")

        df_final_genero = []
        releases_positivas, releases_negativas = [], []

        for appid in appids_genero:
            releases = list(db["steam_news"].find(
                {"appid": appid, "date": {"$gte": limite_data.timestamp()}},
                {"_id": 1, "date": 1, "appid": 1}
            ).sort("date", 1))

            logging.info(f"\nAppID: {appid} - Total de releases encontradas: {len(releases)}")

            if len(releases) < 2:
                logging.info(f"Jogo com AppID {appid} possui releases insuficientes para classificação.")
                continue

            cursor = db["topic_reviews"].find({
                "appid": appid,
                "sentiment": {"$exists": True},
                "datetime_created": {"$gte": limite_data.isoformat()}
            })
            df = pd.DataFrame(list(cursor))
            logging.info(f"• Total de reviews coletadas: {len(df)}")

            if df.empty or "datetime_created" not in df.columns:
                logging.info(f"Nenhum dado de sentimento encontrado para AppID {appid}.")
                continue

            df["datetime_created"] = pd.to_datetime(df["datetime_created"], errors="coerce")
            df = df.dropna(subset=["datetime_created"])

            sent_anterior = None
            threshold = 0.0001
            rows = []

            for curr, nxt in zip(releases, releases[1:]):
                start = datetime.fromtimestamp(curr["date"], tz=timezone.utc)
                end = datetime.fromtimestamp(nxt["date"], tz=timezone.utc)
                intervalo = df[(df["datetime_created"] >= start) & (df["datetime_created"] < end)]

                if intervalo.empty:
                    avg_sent = 0.0
                    label = "no_data"
                    review_count_positive = 0
                    review_count_negative = 0
                    review_count_total = 0
                else:
                    avg_sent = intervalo["sentiment"].mean()
                    review_count_total = len(intervalo)
                    review_count_positive = len(intervalo[intervalo["sentiment"] > 0])
                    review_count_negative = len(intervalo[intervalo["sentiment"] < 0])
                    if sent_anterior is None:
                        label = "neutral" if avg_sent == 0 else ("positive" if avg_sent > 0 else "negative")
                    else:
                        delta = avg_sent - sent_anterior
                        if delta < -threshold:
                            label = "negative"
                        elif delta > threshold:
                            label = "positive"
                        else:
                            label = "neutral"

                if review_count_total > 0 or abs(avg_sent) > 0.001:
                    sent_anterior = avg_sent

                row = {
                    "release_id": str(curr["_id"]),
                    "appid": appid,
                    "release_date": start.strftime("%Y-%m-%d %H:%M:%S"),
                    "avg_sentiment": round(avg_sent, 4),
                    "label": label,
                    "review_count_total": review_count_total,
                    "review_count_positive": review_count_positive,
                    "review_count_negative": review_count_negative
                }
                rows.append(row)

                if label in ["positive", "negative"]:
                    release_doc = db["steam_news"].find_one({"_id": ObjectId(row["release_id"])} , {"contents": 1})
                    if release_doc and "contents" in release_doc:
                        registro = {
                            "release_id": row["release_id"],
                            "contents": release_doc["contents"],
                            "avg_sentiment": row["avg_sentiment"]
                        }
                        (releases_positivas if label == "positive" else releases_negativas).append(registro)

            df_final_genero.extend(rows)

        if not df_final_genero:
            logging.info(f"Gênero '{genero}' não possui dados suficientes para classificação.")
            continue

        df_final = pd.DataFrame(df_final_genero)
        txt_path = os.path.join(RESULTADOS_DIR, f"sentiment_releases_{genero}.txt")
        json_path = os.path.join(RESULTADOS_DIR, f"releases_classificadas_{genero}.json")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(tabulate(df_final, headers="keys", tablefmt="grid"))

        logging.info(tabulate(df_final, headers="keys", tablefmt="grid"))
        logging.info(f"\nArquivo salvo em: {txt_path}")

        verificar_consistencia(db, genero, appids_genero, df_final, limite_data)

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "genero": genero,
                "releases_positivas": releases_positivas,
                "releases_negativas": releases_negativas
            }, f, ensure_ascii=False, indent=2)

        gerar_graficos_review_counts(df_final, genero, RESULTADOS_DIR_GRAFICOS)

        salvar_classificacao_no_mongodb(db, genero, releases_positivas, releases_negativas)

        logging.info("\nJSON gerado com conteúdo das releases:")
        logging.info(f"{json_path}")
        logging.info(f"  • {len(releases_positivas)} releases positivas")
        logging.info(f"  • {len(releases_negativas)} releases negativas")

if __name__ == "__main__":
    main()