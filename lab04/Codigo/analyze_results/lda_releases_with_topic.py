import os
import re
import json
import logging
from datetime import datetime
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from gensim import corpora
from gensim.models.ldamodel import LdaModel
from gensim.models import Phrases
from gensim.models.phrases import Phraser
from pymongo import MongoClient
from bs4 import BeautifulSoup
from gensim.models import CoherenceModel
import matplotlib.pyplot as plt

for package in ["stopwords", "punkt", "wordnet"]:
    try:
        nltk.data.find(f"corpora/{package}" if package != "punkt" else f"tokenizers/{package}")
    except LookupError:
        nltk.download(package, quiet=True)

BASE_DIR = os.path.dirname(__file__)
INPUT_DIR = os.path.join(BASE_DIR, "resultados", "classificacao_release")
OUTPUT_DIR = os.path.join(BASE_DIR, "resultados", "lda_patchnotes")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MONGO_URI = "mongodb+srv://andradelucasmo:Q0I9Yp9Ai6mWK1vI@cluster0.5kddnrk.mongodb.net/"
MONGO_DB = "games"
MONGO_COLLECTION = "lda_patchnotes"

# Logger
logging.basicConfig(
    filename=os.path.join(OUTPUT_DIR, "log_lda_patchnotes.log"),
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def convert_numpy_types(obj):
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(i) for i in obj]
    elif isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(i) for i in obj)
    else:
        return obj

def preprocess_texts(texts):
    stop_words = set(stopwords.words('english')).union(ENGLISH_STOP_WORDS)
    lemmatizer = WordNetLemmatizer()
    processed = []

    for text in texts:
        text = BeautifulSoup(text, "html.parser").get_text()  # remove HTML tags
        text = re.sub(r'http\S+', '', text)  # remove URLs
        text = re.sub(r'[^A-Za-z0-9\s]', '', text)  # remove special characters
        tokens = word_tokenize(text.lower())
        tokens = [word for word in tokens if word.isalpha() and word not in stop_words and len(word) > 2]
        tokens = [lemmatizer.lemmatize(word) for word in tokens]
        processed.append(tokens)

    # Gera bigramas
    phrases = Phrases(processed, min_count=2, threshold=5)
    bigram = Phraser(phrases)
    processed = [bigram[doc] for doc in processed]

    return processed

def process_patchnotes_lda():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]

    arquivos = [f for f in os.listdir(INPUT_DIR) if f.startswith("releases_classificadas_") and f.endswith(".json")]

    for arquivo in arquivos:
        genero = arquivo.replace("releases_classificadas_", "").replace(".json", "")
        logging.info(f"\nGênero: {genero}")

        with open(os.path.join(INPUT_DIR, arquivo), encoding="utf-8") as f:
            data = json.load(f)

        resultado_genero = {
            "genero": genero,
            "data_processo": datetime.now().isoformat(),
        }

        for grupo_nome in ["releases_positivas", "releases_negativas"]:
            textos = [entry["contents"] for entry in data.get(grupo_nome, []) if len(entry.get("contents", "")) > 30]

            if not textos:
                logging.info(f"{grupo_nome}: Nenhum texto válido para LDA.")
                resultado_genero[grupo_nome] = {
                    "quantidade_textos": 0,
                    "topicos": {}
                }
                continue

            processed = preprocess_texts(textos)
            dictionary = corpora.Dictionary(processed)
            dictionary.filter_extremes(no_below=3, no_above=0.5)
            corpus = [dictionary.doc2bow(text) for text in processed]

            if not dictionary or not corpus:
                logging.warning(f"{grupo_nome}: Corpus ou dicionário vazio após processamento.")
                resultado_genero[grupo_nome] = {
                    "quantidade_textos": len(textos),
                    "topicos": {}
                }
                continue

            lda_model = LdaModel(corpus, num_topics=5, id2word=dictionary, passes=10, random_state=42)
            topicos = {}
            for i in range(lda_model.num_topics):
                palavras = lda_model.show_topic(i, topn=10)
                topicos[str(i)] = [p for p, _ in palavras]

            distribuicoes = {}
            for idx, text in enumerate(textos):
                doc_bow = dictionary.doc2bow(processed[idx]) 
                topic_dist = lda_model.get_document_topics(doc_bow)
                distribuicoes[f"release_{idx}"] = topic_dist

            coherence_model = CoherenceModel(
                model=lda_model,
                texts=processed,
                dictionary=dictionary,
                coherence='c_v'
            )
            coerencia = coherence_model.get_coherence()

            resultado_genero[grupo_nome] = {
                "quantidade_textos": len(textos),
                "topicos": topicos,
                "distribuicoes": distribuicoes,
                "coerencia": coerencia
            }

        # Conversão para tipos serializáveis
        resultado_serializavel = convert_numpy_types(resultado_genero)

        output_file = os.path.join(OUTPUT_DIR, f"lda_patchnotes_{genero}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(resultado_serializavel, f, ensure_ascii=False, indent=2)

        # Gráfico de coerência
        GRAFICOS_DIR = os.path.join(OUTPUT_DIR, "graficos")
        os.makedirs(GRAFICOS_DIR, exist_ok=True)

        if "releases_positivas" in resultado_serializavel and "releases_negativas" in resultado_serializavel:
            coerencia_positivas = resultado_serializavel["releases_positivas"].get("coerencia", 0)
            coerencia_negativas = resultado_serializavel["releases_negativas"].get("coerencia", 0)

            plt.figure(figsize=(8, 5))
            plt.bar(
                ["Positivas", "Negativas"],
                [coerencia_positivas, coerencia_negativas],
                color=["green", "red"]
            )
            plt.title(f"Coerência de Tópicos por Positivas/Negativas ({genero})")
            plt.ylabel("Coerência (c_v)")
            plt.savefig(os.path.join(GRAFICOS_DIR, f"coerencia_{genero}.png"))
            plt.close()
        else:
            logging.warning(f"Não foi possível gerar gráfico para {genero}: dados incompletos.")

        try:
            collection.insert_one(resultado_serializavel)
            logging.info(f"LDA salvo no MongoDB e JSON para gênero {genero}")
        except Exception as e:
            logging.error(f"Erro ao inserir no MongoDB: {e}")
            logging.debug(json.dumps(resultado_serializavel, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    process_patchnotes_lda()