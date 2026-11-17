
# nlp_engine.py

import re
from vaderSentiment.vaderSentiment import (
    SentimentIntensityAnalyzer
)

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


analyzer = SentimentIntensityAnalyzer()


def clean_text(text):

    if not isinstance(text, str):
        return ""

    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def analyze_sentiment(text):

    text = clean_text(text)

    return analyzer.polarity_scores(text)


def sentiment_similarity(score1, score2):

    # Convert distance between two compound scores
    # into a similarity score from 0 to 1.

    distance = abs(score1 - score2)

    return max(0, 1 - distance / 2)


def calculate_text_similarity(text1, text2):

    texts = [
        clean_text(text1),
        clean_text(text2)
    ]

    if not any(texts):
        return 0.0

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )

    try:
        matrix = vectorizer.fit_transform(texts)

        similarity = cosine_similarity(
            matrix[0:1],
            matrix[1:2]
        )[0][0]

        return float(similarity)

    except ValueError:
        return 0.0
