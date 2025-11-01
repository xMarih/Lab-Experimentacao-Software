import os
import json
from pymongo import MongoClient

MONGO_URI = "mongodb+srv://andradelucasmo:Q0I9Yp9Ai6mWK1vI@cluster0.5kddnrk.mongodb.net/"
MONGO_DB = "games"
NOME_COLLECTION = "top_sellers_info"

def importar_json_para_mongodb():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    caminho_arquivo = os.path.join(base_dir, "resultado_top_sellers_with_info.json")

    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]

    if not os.path.exists(caminho_arquivo):
        print(f"Arquivo '{caminho_arquivo}' não encontrado.")
        return

    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        try:
            dados = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Erro ao ler JSON: {e}")
            return

    if not isinstance(dados, list):
        print("O JSON não contém uma lista no nível superior.")
        return

    if dados:
        db[NOME_COLLECTION].delete_many({})
        db[NOME_COLLECTION].insert_many(dados)
        print(f"Inseridos {len(dados)} documentos na collection '{NOME_COLLECTION}'")
    else:
        print("Nenhum dado encontrado para inserir.")

if __name__ == "__main__":
    importar_json_para_mongodb()