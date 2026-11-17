from recommender import recommend_movies
from tmdb_api import (
    get_movie_details,
    get_movie_credits,
    get_movie_keywords,
    discover_movies
)

from nlp_engine import calculate_text_similarity

movie_a = """
Science fiction movie about space exploration,
astronauts and the future of humanity.
"""

movie_b = """
Astronauts travel through space and explore
new worlds to save humanity.
"""

movie_c = """
A romantic comedy about marriage,
relationships and family life.
"""

similarity_ab = calculate_text_similarity(
    movie_a, movie_b
)

similarity_ac = calculate_text_similarity(
    movie_a, movie_c
)

print("Movie A vs Movie B:", similarity_ab)

print("Movie A vs Movie C:", similarity_ac)

assert 0 <= similarity_ab <= 1

assert 0 <= similarity_ac <= 1

assert similarity_ab > similarity_ac

print("TF-IDF test passed!")

from nlp_engine import analyze_sentiment

positive_text = (
    "A wonderful and inspiring story "
    "about hope, love and happiness."
)

negative_text = (
    "A terrible and tragic story "
    "filled with fear and sadness."
)

positive = analyze_sentiment(positive_text)

negative = analyze_sentiment(negative_text)

print("Positive sentiment:", positive)

print("Negative sentiment:", negative)

assert positive["compound"] > negative["compound"]

print("Sentiment analysis passed!")

scores = [
    item["scores"]["final"]
    for item in recommendations
]

assert scores == sorted(scores, reverse=True)

for item in recommendations:

    score = item["scores"]

    assert 0 <= score["content"] <= 1
    assert 0 <= score["sentiment"] <= 1
    assert 0 <= score["quality"] <= 1
    assert 0 <= score["final"] <= 1

print("Hybrid recommendation test passed!")

# Reference movie: Interstellar

movie_id = 157336

details = get_movie_details(movie_id)

credits = get_movie_credits(movie_id)

keywords = get_movie_keywords(movie_id)

# Retrieve cast
cast = [
    person["name"]
    for person in credits.get("cast", [])[:5]
]

# Retrieve director
director = next(
    (
        person["name"]
        for person in credits.get("crew", [])
        if person.get("job") == "Director"
    ),
    ""
)

# Retrieve genres
genres = [
    genre["name"]
    for genre in details.get("genres", [])
]

# Create reference movie dictionary
selected_movie = {
    "id": movie_id,
    "title": details.get("title", ""),
    "overview": details.get("overview", ""),
    "genres": genres,
    "keywords": [
        keyword["name"] for keyword in keywords
    ],
    "cast": cast,
    "director": director,
    "vote_average": details.get("vote_average", 0),
    "vote_count": details.get("vote_count", 0)
}

# Retrieve candidate movies

data = discover_movies({
    "sort_by": "popularity.desc",
    "vote_count.gte": 100,
    "vote_average.gte": 5,
    "with_genres": 878
})

candidate_movies = []

for movie in data:

    try:

        movie_details = get_movie_details(
            movie["id"]
        )

        movie_credits = get_movie_credits(
            movie["id"]
        )

        movie_keywords = get_movie_keywords(
            movie["id"]
        )

        movie_cast = [
            person["name"]
            for person in movie_credits.get("cast", [])[:5]
        ]

        movie_director = next(
            (
                person["name"]
                for person in movie_credits.get("crew", [])
                if person.get("job") == "Director"
            ),
            ""
        )

        candidate_movies.append({
            "id": movie["id"],
            "title": movie_details.get("title", ""),
            "overview": movie_details.get("overview", ""),
            "genres": [
                genre["name"]
                for genre in movie_details.get("genres", [])
            ],
            "keywords": [
                keyword["name"]
                for keyword in movie_keywords
            ],
            "cast": movie_cast,
            "director": movie_director,
            "vote_average": movie_details.get("vote_average", 0),
            "vote_count": movie_details.get("vote_count", 0)
        })

    except Exception as error:

        print("Could not retrieve movie:", error)

# Generate hybrid recommendations

recommendations = recommend_movies(
    selected_movie,
    candidate_movies,
    top_n=10
)

print("\nHYBRID RECOMMENDATIONS")

for item in recommendations:

    movie = item["movie"]
    score = item["scores"]

    print("\nMovie:", movie["title"])

    print("Content similarity:", round(score["content"], 3))

    print("Sentiment similarity:", round(score["sentiment"], 3))

    print("Quality score:", round(score["quality"], 3))

    print("Final score:", round(score["final"], 3))

# Verify recommendation results

scores = [
    item["scores"]["final"]
    for item in recommendations
]

# Verify movies are ranked in descending order

assert scores == sorted(scores, reverse=True)

# Verify scores are between 0 and 1

for item in recommendations:

    score = item["scores"]

    assert 0 <= score["content"] <= 1
    assert 0 <= score["sentiment"] <= 1
    assert 0 <= score["quality"] <= 1
    assert 0 <= score["final"] <= 1

# Verify Interstellar is not recommended itself

assert all(
    item["movie"]["id"] != selected_movie["id"]
    for item in recommendations
)

print("\nHYBRID RECOMMENDATION TEST PASSED!")

import requests

response = requests.get(
    "https://api.themoviedb.org/3/movie/popular",
    headers={
        "Authorization": "Bearer INVALID_TEST_TOKEN"
    },
    timeout=20
)

print("Status:", response.status_code)
print(response.text)