
# recommender.py

from nlp_engine import (
    clean_text,
    analyze_sentiment,
    sentiment_similarity,
    calculate_text_similarity
)


def movie_feature_text(movie):

    genres = movie.get("genres", [])
    keywords = movie.get("keywords", [])
    cast = movie.get("cast", [])
    director = movie.get("director", "")

    genre_text = " ".join(genres)
    keyword_text = " ".join(keywords)
    cast_text = " ".join(cast[:5])

    overview = movie.get("overview", "")

    return " ".join([
        genre_text,
        keyword_text,
        cast_text,
        director,
        overview
    ])


def quality_score(movie):

    rating = float(movie.get("vote_average", 0) or 0)
    votes = int(movie.get("vote_count", 0) or 0)

    # Bayesian-style quality adjustment
    # Reduces the influence of movies with very few votes.

    minimum_votes = 100
    average_rating = 6.5

    score = (
        votes / (votes + minimum_votes) * rating
        +
        minimum_votes / (votes + minimum_votes)
        * average_rating
    )

    return max(0, min(score / 10, 1))


def hybrid_similarity(movie_a, movie_b):

    text_a = movie_feature_text(movie_a)
    text_b = movie_feature_text(movie_b)

    content_score = calculate_text_similarity(
        text_a,
        text_b
    )

    sentiment_a = analyze_sentiment(
        movie_a.get("overview", "")
    )["compound"]

    sentiment_b = analyze_sentiment(
        movie_b.get("overview", "")
    )["compound"]

    sentiment_score = sentiment_similarity(
        sentiment_a,
        sentiment_b
    )

    quality = quality_score(movie_b)

    final_score = (
        0.60 * content_score
        + 0.20 * sentiment_score
        + 0.20 * quality
    )

    return {
        "content": content_score,
        "sentiment": sentiment_score,
        "quality": quality,
        "final": final_score
    }


def recommend_movies(
    selected_movie,
    candidate_movies,
    top_n=10
):

    results = []

    for movie in candidate_movies:

        if movie["id"] == selected_movie["id"]:
            continue

        scores = hybrid_similarity(
            selected_movie,
            movie
        )

        results.append({
            "movie": movie,
            "scores": scores
        })

    results.sort(
        key=lambda x: x["scores"]["final"],
        reverse=True
    )

    return results[:top_n]


def natural_language_match(
    query,
    movies,
    top_n=10
):

    query = clean_text(query)

    query_sentiment = analyze_sentiment(query)[
        "compound"
    ]

    results = []

    for movie in movies:

        features = movie_feature_text(movie)

        content = calculate_text_similarity(
            query,
            features
        )

        movie_sentiment = analyze_sentiment(
            movie.get("overview", "")
        )["compound"]

        sentiment = sentiment_similarity(
            query_sentiment,
            movie_sentiment
        )

        score = 0.80 * content + 0.20 * sentiment

        results.append({
            "movie": movie,
            "score": score
        })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results[:top_n]
