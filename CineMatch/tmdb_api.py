
# tmdb_api.py

import requests
import streamlit as st

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"


def get_headers():
    token = st.secrets.get("TMDB_ACCESS_TOKEN", "")

    if not token:
        raise ValueError("TMDB API token is missing.")

    return {
        "Authorization": f"Bearer {token}",
        "accept": "application/json"
    }


@st.cache_data(ttl=3600)
def tmdb_get(endpoint, params=None):
    """Make a cached request to the TMDB API."""

    url = f"{BASE_URL}/{endpoint.lstrip('/')}"

    response = requests.get(
        url,
        headers=get_headers(),
        params=params or {},
        timeout=20
    )

    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=3600)
def get_genres():

    data = tmdb_get("genre/movie/list")

    return {
        item["name"]: item["id"]
        for item in data["genres"]
    }


@st.cache_data(ttl=1800)
def get_trending():

    data = tmdb_get("trending/movie/week")

    return data.get("results", [])


@st.cache_data(ttl=3600)
def discover_movies(params, page=1):

    query = dict(params)
    query["page"] = page

    data = tmdb_get("discover/movie", query)

    return data.get("results", [])


@st.cache_data(ttl=3600)
def search_movie(query):

    data = tmdb_get(
        "search/movie",
        {"query": query}
    )

    return data.get("results", [])


@st.cache_data(ttl=3600)
def get_movie_details(movie_id):

    return tmdb_get(f"movie/{movie_id}")


@st.cache_data(ttl=3600)
def get_movie_credits(movie_id):

    return tmdb_get(f"movie/{movie_id}/credits")


@st.cache_data(ttl=3600)
def get_movie_keywords(movie_id):

    data = tmdb_get(f"movie/{movie_id}/keywords")

    return data.get("keywords", [])


@st.cache_data(ttl=3600)
def get_movie_certification(movie_id):

    data = tmdb_get(f"movie/{movie_id}/release_dates")

    for country in data.get("results", []):

        if country.get("iso_3166_1") == "CA":
            for release in country.get("release_dates", []):
                certification = release.get("certification")

                if certification:
                    return certification

    return "Not available"


def get_image_url(path):

    if not path:
        return None

    return f"{IMAGE_BASE}{path}"

@st.cache_data(ttl=3600)
def search_person(name):

    data = tmdb_get(
        "search/person",
        {"query": name}
    )

    return data.get("results", [])


def build_movie_filters(
    start_year=2000,
    end_year=2026,
    min_rating=0,
    min_votes=0,
    min_runtime=0,
    max_runtime=300,
    language="en",
    genre_ids=None,
    genre_logic="AND",
    actor_id=None,
    director_id=None,
    certification=None
):

    params = {
        "sort_by": "popularity.desc",
        "include_adult": "false",
        "include_video": "false",
        "primary_release_date.gte":
            f"{start_year}-01-01",
        "primary_release_date.lte":
            f"{end_year}-12-31",
        "vote_average.gte": min_rating,
        "vote_count.gte": min_votes,
        "with_runtime.gte": min_runtime,
        "with_runtime.lte": max_runtime,
        "with_original_language": language,
    }

    if genre_ids:

        separator = "," if genre_logic == "AND" else "|"

        params["with_genres"] = separator.join(
            str(x) for x in genre_ids
        )

    if actor_id:
        params["with_cast"] = actor_id

    if director_id:
        params["with_crew"] = director_id

    if certification:
        params["certification_country"] = "US"
        params["certification"] = certification

    return params

def test_api_connection():

    data = tmdb_get("movie/popular")

    print("API CONNECTION SUCCESSFUL")

    print("Total movies:", data["total_results"])

    print("First movie:", data["results"][0]["title"])

    return data