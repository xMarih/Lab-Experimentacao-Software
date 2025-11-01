import os
import re
import json
import logging
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
import numpy as np
from gensim.models import CoherenceModel
from gensim.models.phrases import Phraser
from gensim.models import Phrases
from gensim import corpora

# Diretórios
BASE_DIR = os.path.dirname(__file__)
INPUT_DIR_LDA_PATCHNOTES = os.path.join(BASE_DIR, "resultados/lda_patchnotes")
INPUT_DIR_CLASSIFICACAO = os.path.join(BASE_DIR, "resultados/classificacao_release")
OUTPUT_DIR = os.path.join(BASE_DIR, "resultados/coerencia")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Logging
log_path = os.path.join(OUTPUT_DIR, "log_coherence.log")
logging.basicConfig(
    filename=log_path,
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def filtrar_por_tfidf(topicos, cutoff_percentile=30):
    docs = [' '.join(t) for t in topicos]
    
    vectorizer = CountVectorizer()
    tfidf = TfidfTransformer()
    X = vectorizer.fit_transform(docs)
    X_tfidf = tfidf.fit_transform(X)
    
    words = vectorizer.get_feature_names_out()
    
    word_scores = np.array(X_tfidf.mean(axis=0)).flatten()
    threshold = np.percentile(word_scores, cutoff_percentile)
    
    important_words = set(words[word_scores > threshold])
    
    return [[w for w in t if w in important_words] for t in topicos]

def preprocess_texts(texts):
    stop_words = set(stopwords.words('english')).union(ENGLISH_STOP_WORDS)
    lemmatizer = WordNetLemmatizer()
    processed = []

    for text in texts:
        text = BeautifulSoup(text, "html.parser").get_text()
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'[^A-Za-z0-9\s]', '', text)
        tokens = word_tokenize(text.lower())
        tokens = [word for word in tokens if word.isalpha() and word not in stop_words and len(word) > 2]
        tokens = [lemmatizer.lemmatize(word) for word in tokens]
        processed.append(tokens)

    phrases = Phrases(processed, min_count=2, threshold=5)
    bigram = Phraser(phrases)
    processed = [bigram[doc] for doc in processed]

    return processed

def preparar_dados():

    arquivos_releases_classificadas = [
        f for f in os.listdir(INPUT_DIR_CLASSIFICACAO) 
        if f.startswith("releases_classificadas_") and f.endswith(".json")
    ]

    dados_por_genero = {}
    for arquivo in arquivos_releases_classificadas:
        genero = arquivo.replace("releases_classificadas_", "").replace(".json", "")
        caminho_arquivo = os.path.join(INPUT_DIR_CLASSIFICACAO, arquivo)

        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            dados_classificacao = json.load(f)

        def processar_textos(grupo_nome):
            textos = [entry["contents"] for entry in dados_classificacao.get(grupo_nome, []) if len(entry.get("contents", "")) > 30]
            processed = preprocess_texts(textos)
            dictionary = corpora.Dictionary(processed)
            dictionary.filter_extremes(no_below=3, no_above=0.5)
            return processed, dictionary
        
        caminho_lda = os.path.join(INPUT_DIR_LDA_PATCHNOTES, f"lda_patchnotes_{genero}.json")
        with open(caminho_lda, "r", encoding="utf-8") as f:
            dados_lda = json.load(f)
        
        topicos_positivos = list(dados_lda["releases_positivas"]["topicos"].values())
        topicos_negativos = list(dados_lda["releases_negativas"]["topicos"].values())

        textos_positivos, dictionary_positivo = processar_textos("releases_positivas")
        textos_negativos, dictionary_negativo = processar_textos("releases_negativas")

        dados_por_genero[genero] = {
            "positivas": {
                "topicos": topicos_positivos,
                "textos": textos_positivos,
                "dicionario": dictionary_positivo,
            },
            "negativas": {
                "topicos": topicos_negativos,
                "textos": textos_negativos,
                "dicionario": dictionary_negativo,
            }
        }

    return dados_por_genero

def calcular_coerencia(dados_por_genero):
    metricas = ['c_v', 'u_mass', 'c_uci', 'c_npmi']

    resultados = {}
    for genero, dados in dados_por_genero.items():
        resultados[genero] = {
            "positivas": {metric: None for metric in metricas},
            "negativas": {metric: None for metric in metricas}
        }
        for tipo in ["positivas", "negativas"]:
            topicos = dados[tipo]["topicos"]
            textos = dados[tipo]["textos"]
            dictionary = dados[tipo]["dicionario"]
            
            topicos_filtrados = filtrar_por_tfidf(topicos)
            
            topicos_filtrados = [t for t in topicos_filtrados if len(t) >= 2]
            
            for metric in metricas:
                try:
                    coherence_model = CoherenceModel(
                        topics=topicos_filtrados,
                        texts=textos,
                        dictionary=dictionary,
                        coherence=metric
                    )
                    resultados[genero][tipo][metric] = coherence_model.get_coherence()
                except Exception as e:
                    logging.error(f"Erro na métrica {metric} para {genero}/{tipo}: {str(e)}")
                    resultados[genero][tipo][metric] = None
    
    with open(os.path.join(OUTPUT_DIR, "coerencia_resultados.json"), "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    return resultados
    

def main():
    dados = preparar_dados()
    resultados_coerencia = calcular_coerencia(dados)
    logging.info(f"Resultados de coerência: {json.dumps(resultados_coerencia, indent=2)}")

if __name__ == "__main__":
    main()