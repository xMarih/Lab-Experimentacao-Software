import re
from datetime import datetime, timezone
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from gensim import corpora
from gensim.models.ldamodel import LdaModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from mongo_client import get_reviews_from_mongo

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

def preprocess_texts_with_lemmatization(texts):
    stop_words = set(stopwords.words('english')).union(ENGLISH_STOP_WORDS)
    lemmatizer = WordNetLemmatizer()
    processed = []

    for text in texts:
        text = re.sub(r'http\S+', '', text)  # Remove URLs
        text = re.sub(r'[^A-Za-z0-9\s]', '', text)  # Remove caracteres não alfanuméricos
        tokens = word_tokenize(text.lower())  # Tokenização
        tokens = [word for word in tokens if word.isalpha() and word not in stop_words and len(word) > 2]
        tokens = [lemmatizer.lemmatize(word) for word in tokens]
        processed.append(tokens)

    return processed

def process_reviews_with_lda():

    raw_data = get_reviews_from_mongo(20)
    print(f"Total de reviews com pelo menos 20 caracteres: {len(raw_data)}")

    if not raw_data:
        print("Nenhuma review encontrada. Encerrando.")
        return

    # Preparar corpus
    processed_reviews = preprocess_texts_with_lemmatization([r["review"] for r in raw_data])
    dictionary = corpora.Dictionary(processed_reviews)
    dictionary.filter_extremes(no_below=10, no_above=0.1)
    corpus = [dictionary.doc2bow(text) for text in processed_reviews]

    # Treinar modelo LDA
    lda_model = LdaModel(corpus, num_topics=5, id2word=dictionary, passes=15, random_state=42)

    # Exibir tópicos
    topics = {}
    print("\nTópicos identificados pelo LDA:")
    for i in range(lda_model.num_topics):
        words = lda_model.show_topic(i, topn=10)
        keywords = ", ".join([word for word, _ in words])
        topics[i] = keywords
        print(f"Tópico {i}: {keywords}")


    # Análise de sentimento
    sia = SentimentIntensityAnalyzer()
    review_data = []

    for review_obj, bow in zip(raw_data, corpus):
        topic_distribution = lda_model.get_document_topics(bow)
        best_topic = max(topic_distribution, key=lambda x: x[1])[0]
        sentiment_scores = sia.polarity_scores(review_obj["review"])
        compound_sentiment = sentiment_scores["compound"]

        # Classificação textual do sentimento
        if compound_sentiment > 0:
            sentiment_label = "positive"
        elif compound_sentiment < 0:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"

        review_data.append({
            "review": review_obj["review"],
            "datetime_created": datetime.fromtimestamp(
                review_obj["timestamp_created"], timezone.utc
            ).isoformat() if review_obj.get("timestamp_created") else None,
            "recommendationid": review_obj.get("recommendationid"),
            "topic": best_topic,
            "sentiment": compound_sentiment,
            "sentiment_label": sentiment_label,
            "appid": review_obj.get("appid")
        })

    print(f"\nTotal de reviews atribuídas: {len(review_data)}")

    return topics, review_data