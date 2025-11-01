import os
import pandas as pd
from pymongo import MongoClient
from collections import defaultdict

MONGO_URI = "mongodb+srv://andradelucasmo:Q0I9Yp9Ai6mWK1vI@cluster0.5kddnrk.mongodb.net/"
MONGO_DB = "games"
MONGO_COLLECTION = "dados_jogos"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIRETORIO_CSV = os.path.join(BASE_DIR, "arquivos_jogos")

def importar_csvs_para_mongodb(diretorio):
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]

    for arquivo in os.listdir(diretorio):
        if not arquivo.endswith(".csv"):
            continue

        caminho_arquivo = os.path.join(diretorio, arquivo)
        nome_arquivo = os.path.splitext(arquivo)[0]

        try:
            partes = nome_arquivo.split("_")
            genero = partes[0]
            appid = int(partes[1])
        except (IndexError, ValueError):
            print(f"⚠️ Nome de arquivo inválido para extração: {arquivo}")
            continue

        print(f"Inserindo dados de '{arquivo}' (genero: {genero}, appid: {appid})...")

        try:
            df = pd.read_csv(caminho_arquivo)
            if df.empty:
                print("Arquivo vazio. Nenhum dado inserido.")
                continue

            # Adicionar campos fixos
            df["genero"] = genero
            df["appid"] = appid

            registros = df.to_dict(orient="records")
            collection.insert_many(registros)

            print(f"Inseridos {len(registros)} documentos em '{MONGO_COLLECTION}'")
        except Exception as e:
            print(f"Erro ao processar '{arquivo}': {e}")

    print("\nImportação concluída.")
    verificar_consistencia_dados()


def verificar_consistencia_dados():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]

    print(f"Verificando variações de colunas globalmente na collection '{MONGO_COLLECTION}'...\n")

    variacoes = defaultdict(list)  # chave: colunas, valor: lista de gêneros

    for doc in collection.find({}, {"_id": 0}):
        colunas = tuple(sorted(doc.keys()))
        genero = doc.get("genero", "indefinido")
        variacoes[colunas].append(genero)

    if len(variacoes) == 1:
        total_docs = sum(len(gens) for gens in variacoes.values())
        print(f"Todos os {total_docs} documentos possuem o mesmo conjunto de colunas.")
    else:
        print(f"Foram encontradas {len(variacoes)} variações de colunas na collection:\n")
        for i, (colunas, generos) in enumerate(variacoes.items(), 1):
            print(f"🔹 Variação {i}: ({len(generos)} documentos)")
            print("   • Gêneros presentes:", ", ".join(sorted(set(generos))))
            print("   • Colunas:")
            for col in colunas:
                print(f"     - {col}")
            print("-" * 50)

if __name__ == "__main__":
    importar_csvs_para_mongodb(DIRETORIO_CSV)


