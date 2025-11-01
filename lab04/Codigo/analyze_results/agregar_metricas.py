import pandas as pd
import os
from pymongo import MongoClient
from datetime import datetime, timedelta

MONGO_URI = "mongodb+srv://andradelucasmo:Q0I9Yp9Ai6mWK1vI@cluster0.5kddnrk.mongodb.net/"
MONGO_DB = "games"
DIAS_LIMITE = 365

def get_db():
    return MongoClient(MONGO_URI)[MONGO_DB]

def salvar_csv(df, nome_base, genero):
    base_dir = os.path.dirname(__file__)
    resultados_dir = os.path.join(base_dir, "resultados/dados_agregados")
    os.makedirs(resultados_dir, exist_ok=True)

    nome = f"{nome_base}_{genero}.csv"
    caminho = os.path.join(resultados_dir, nome)
    df.to_csv(caminho, index=False)
    print(f"Arquivo salvo em: {caminho}")

def obter_releases_por_data(appids):
    db = get_db()
    cursor = db["steam_news"].find({
        "date": {"$exists": True},
        "appid": {"$in": appids}
    }, {"date": 1})
    df = pd.DataFrame(list(cursor))

    if df.empty:
        return pd.DataFrame(columns=['date', 'release'])

    df["date"] = pd.to_datetime(df["date"], unit="s", errors="coerce").dt.date
    limite = datetime.now().date() - timedelta(days=DIAS_LIMITE)
    df = df[df['date'] >= limite]
    return df.groupby("date").size().reset_index(name="release")

def gerar_csv_por_genero():
    db = get_db()
    df = pd.DataFrame(list(db["dados_jogos"].find({})))

    if df.empty or "genero" not in df.columns or "appid" not in df.columns:
        print("Collection 'dados_jogos' vazia ou sem as colunas obrigatórias.")
        return

    df.columns = df.columns.str.strip()
    df = df.drop(columns=["_id"], errors="ignore")

    # Detectar coluna de data
    coluna_data = None
    for col in ["DateTime", "Date"]:
        if col in df.columns:
            coluna_data = col
            break

    if not coluna_data:
        print("Nenhuma coluna de data encontrada.")
        return

    # Preparar dados
    df[coluna_data] = pd.to_datetime(df[coluna_data], errors="coerce")
    df["date"] = df[coluna_data].dt.date
    limite = datetime.now().date() - timedelta(days=DIAS_LIMITE)
    df = df[df["date"] >= limite]

    colunas_valores = ["Players", "Followers", "Positive reviews", "Negative reviews"]
    colunas_existentes = [col for col in colunas_valores if col in df.columns]

    for genero, grupo in df.groupby("genero"):
        appids_genero = grupo["appid"].unique().tolist()

        # Agregar métricas
        grupo_agregado = grupo[["date"] + colunas_existentes].copy()
        grupo_agregado = grupo_agregado.groupby("date").mean().reset_index().sort_values("date")

        # Diferença diária
        for col in colunas_existentes:
            grupo_agregado[col] = grupo_agregado[col].diff()

        # Releases por appid
        releases_df = obter_releases_por_data(appids_genero)
        grupo_agregado = grupo_agregado.merge(releases_df, on="date", how="left")
        grupo_agregado["Release"] = grupo_agregado["release"].fillna(0).astype(int)
        grupo_agregado = grupo_agregado.drop(columns=["release"], errors="ignore")

        # Sentimento médio por appid
        sentiment_df = pd.DataFrame(list(db["topic_reviews"].find({
            "sentiment": {"$exists": True},
            "appid": {"$in": appids_genero},
            "datetime_created": {"$gte": limite.isoformat()}
        }, {"datetime_created": 1, "sentiment": 1, "sentiment_label": 1})))

        if not sentiment_df.empty:
            sentiment_df["date"] = pd.to_datetime(sentiment_df["datetime_created"], errors="coerce").dt.date
            # Sentimento médio
            sentimento_medio = sentiment_df.groupby("date")["sentiment"].mean().reset_index(name="Sentiment")
            grupo_agregado = grupo_agregado.merge(sentimento_medio, on="date", how="left")

            # Contagem por sentimento_label
            contagem_labels = sentiment_df[sentiment_df["sentiment_label"].isin(["positive", "negative"])]
            contagem = pd.crosstab(contagem_labels["date"], contagem_labels["sentiment_label"])
            contagem = contagem.rename(columns={
                "positive": "PositiveReviewCount",
                "negative": "NegativeReviewCount"
            }).reset_index()

            grupo_agregado = grupo_agregado.merge(contagem, on="date", how="left")

        # Colunas finais
        colunas_saida = ["date"] + colunas_existentes + ["Release"]
        if "Sentiment" in grupo_agregado.columns:
            colunas_saida.append("Sentiment")
        if "PositiveReviewCount" in grupo_agregado.columns:
            colunas_saida.append("PositiveReviewCount")
        if "NegativeReviewCount" in grupo_agregado.columns:
            colunas_saida.append("NegativeReviewCount")

        df_final = grupo_agregado[colunas_saida]
        salvar_csv(df_final, "dados_agregados", genero)

if __name__ == "__main__":
    gerar_csv_por_genero()