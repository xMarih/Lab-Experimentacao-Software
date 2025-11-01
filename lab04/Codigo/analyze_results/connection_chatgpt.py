import os
import json
import logging
import requests
from pymongo import MongoClient

# Diretório base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTADOS_DIR = os.path.join(BASE_DIR, "resultados")
RESPOSTAS_DIR = os.path.join(RESULTADOS_DIR, "respostas_chatgpt")
os.makedirs(RESPOSTAS_DIR, exist_ok=True)

# Configuração do log dentro da pasta de respostas
LOG_FILE = os.path.join(RESPOSTAS_DIR, "envio_payloads.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Conexão com MongoDB
MONGO_URI = "mongodb+srv://andradelucasmo:Q0I9Yp9Ai6mWK1vI@cluster0.5kddnrk.mongodb.net/"
DB_NAME = "games"
RELEASES_COLLECTION = "releases_classificadas_json"
LDA_COLLECTION = "lda_patchnotes"
RESPOSTAS_COLLECTION = "respostas_chatgpt"

# Webhook da API
WEBHOOK_URL = "https://n8nwebhook.psmotta.cloud/webhook/TIS6-teste-one-shot"
AUTH = ("LDA", "testelda")
HEADERS = {"Content-Type": "application/json"}

def enviar_payloads():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    generos = db[LDA_COLLECTION].distinct("genero")
    for genero in generos:
        try:
            logging.info(f"Processando gênero: {genero}")

            lda_doc = db[LDA_COLLECTION].find_one({"genero": genero})
            release_doc = db[RELEASES_COLLECTION].find_one({"genero": genero})

            if not lda_doc or not release_doc:
                logging.warning(f"Dados ausentes para o gênero {genero}")
                continue

            positivas = release_doc.get("releases_positivas", [])
            negativas = release_doc.get("releases_negativas", [])

            if not positivas or not negativas:
                logging.warning(f"Sem releases suficientes para o gênero {genero}")
                continue

            # Seleciona a release mais positiva (maior avg_sentiment)
            release_pos = sorted(
                positivas, key=lambda x: x.get("avg_sentiment", 0), reverse=True
            )[0]
            release_pos["label"] = "positive"

            # Seleciona a release mais negativa (menor avg_sentiment)
            release_neg = sorted(
                negativas, key=lambda x: x.get("avg_sentiment", 0)
            )[0]
            release_neg["label"] = "negative"

            payload = {
                "releases": [release_pos, release_neg],
                "genero": lda_doc.get("genero"),
                "data_processo": lda_doc.get("data_processo"),
                "releases_positivas": lda_doc.get("releases_positivas"),
                "releases_negativas": lda_doc.get("releases_negativas")
            }

            logging.info(f"Enviando payload para {genero}...")
            logging.info(json.dumps(payload, indent=2, ensure_ascii=False))

            response = requests.post(WEBHOOK_URL, auth=AUTH, headers=HEADERS, json=payload)

            if response.status_code == 200:
                resultado = response.json()

                # Salva localmente
                output_path = os.path.join(RESPOSTAS_DIR, f"resposta_{genero}.json")
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(resultado, f, ensure_ascii=False, indent=4)

                # Salva no MongoDB
                db[RESPOSTAS_COLLECTION].insert_one(resultado)

                logging.info(f"Resposta salva com sucesso para {genero} em {output_path}")
            else:
                logging.error(f"Erro HTTP {response.status_code} para {genero}: {response.text}")

        except Exception as e:
            logging.exception(f"Erro ao processar gênero {genero}: {e}")

if __name__ == "__main__":
    enviar_payloads()