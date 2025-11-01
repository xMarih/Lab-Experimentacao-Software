import os
import re
import json
import logging
from datetime import datetime
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

# Configuração inicial
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

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

            resultado_genero[grupo_nome] = {
                "quantidade_textos": len(textos),
                "topicos": topicos
            }

        output_file = os.path.join(OUTPUT_DIR, f"lda_patchnotes_{genero}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(resultado_genero, f, ensure_ascii=False, indent=2)

        try:
            collection.insert_one(resultado_genero)
            logging.info(f"LDA salvo no MongoDB e JSON para gênero {genero}")
        except Exception as e:
            logging.error(f"Erro ao inserir no MongoDB: {e}")
            logging.debug(json.dumps(resultado_genero, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    process_patchnotes_lda()