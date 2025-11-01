#!/usr/bin/env python3
"""
Consulta todas as coleções do banco Mongo e exporta cada coleção para um CSV

Uso:
  python query_and_csv.py

Configuração de conexão (usa variáveis de ambiente se definidas):
  MONGO_URI (default: mongodb://admin:password@localhost:27018/)
  MONGO_DB  (default: games)

Os CSVs são salvos em ./exports/ (dentro do diretório deste arquivo).
"""
import os
import sys
from pymongo import MongoClient
from bson import ObjectId
from bson.decimal128 import Decimal128
import datetime
import pandas as pd


def convert_bson_types(value):
    """Recursively converte tipos BSON para valores serializáveis (str, isoformat, float).
    """
    # ObjectId
    if isinstance(value, ObjectId):
        return str(value)
    # Decimal128
    if isinstance(value, Decimal128):
        try:
            return float(value.to_decimal())
        except Exception:
            return str(value)
    # datetime
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.isoformat()
    # dict -> recursivo
    if isinstance(value, dict):
        return {k: convert_bson_types(v) for k, v in value.items()}
    # list/tuple -> recursivo
    if isinstance(value, (list, tuple)):
        return [convert_bson_types(v) for v in value]
    # outros tipos (int, float, str, bool, None)
    return value


def export_collections_to_csv(uri, db_name, out_dir=None):
    out_dir = out_dir or os.path.join(os.path.dirname(__file__), "exports")
    os.makedirs(out_dir, exist_ok=True)

    print(f"Conectando em: {uri}  banco: {db_name}")
    client = MongoClient(uri)
    db = client[db_name]

    collections = db.list_collection_names()
    if not collections:
        print(f"Nenhuma coleção encontrada no banco '{db_name}'.")
        return

    print(f"Coleções encontradas: {collections}")

    for coll_name in collections:
        print(f"\nProcessando coleção: {coll_name}")
        coll = db[coll_name]
        total = coll.count_documents({})
        print(f"Total de documentos: {total}")

        if total == 0:
            print("Coleção vazia — pulando.")
            continue

        # carregar documentos (cuidado com coleções muito grandes)
        docs_cursor = coll.find({})
        docs = []
        for d in docs_cursor:
            # converter _id e outros tipos BSON
            docs.append(convert_bson_types(d))

        # normalizar para DataFrame (achata dicionários aninhados)
        try:
            df = pd.json_normalize(docs)
        except Exception as e:
            print(f"Erro ao normalizar documentos da coleção {coll_name}: {e}")
            # fallback: criar DataFrame simples com representação string
            df = pd.DataFrame([{k: str(v) for k, v in doc.items()} for doc in docs])

        out_path = os.path.join(out_dir, f"{coll_name}.csv")
        try:
            df.to_csv(out_path, index=False, encoding="utf-8-sig")
            print(f"Exportado: {out_path}  (linhas: {len(df)})")
        except Exception as e:
            print(f"Falha ao salvar CSV para {coll_name}: {e}")


def main():
    # Ler variáveis de ambiente com fallback
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:password@localhost:27018/")
    MONGO_DB = os.getenv("MONGO_DB", "games")
    OUT_DIR = os.getenv("EXPORT_DIR", None)

    try:
        export_collections_to_csv(MONGO_URI, MONGO_DB, OUT_DIR)
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
