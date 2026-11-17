import streamlit as st

from tmdb_api import test_api_connection

result = test_api_connection()

st.write("TMDB API connection successful!")
st.write("Total results:", result["total_results"])
st.write("First movie:", result["results"][0]["title"])

from tmdb_api import get_trending

movies = get_trending()

print("Number of movies:", len(movies))

for movie in movies[:5]:

    print("Title:", movie.get("title"))
    print("Date:", movie.get("release_date"))
    print("Rating:", movie.get("vote_average"))
    print("------------------")

from tmdb_api import get_movie_credits

movie_id = 157336

credits = get_movie_credits(movie_id)

print("CAST:")

for person in credits["cast"][:5]:
    print(person["name"], "-", person["character"])

print("\nDIRECTOR:")

for person in credits["crew"]:

    if person["job"] == "Director":
        print(person["name"])

from tmdb_api import get_movie_keywords

keywords = get_movie_keywords(157336)

print("MOVIE KEYWORDS:")

for keyword in keywords:
    print(keyword["name"])

from tmdb_api import get_movie_certification

certification = get_movie_certification(157336)

print("Canadian Certification:", certification)

for movie in results:

    year = int(movie["release_date"][:4])

    assert 2010 <= year <= 2020

print("Year filter passed!")

for movie in results:

    assert movie["vote_average"] >= 7.0

print("Rating filter passed!")

for movie in results:

    assert movie["vote_count"] >= 500

print("Vote count filter passed!")

from tmdb_api import get_movie_details

for movie in results:

    details = get_movie_details(movie["id"])

    runtime = details.get("runtime")

    if runtime is not None:

        assert 90 <= runtime <= 150

print("Runtime filter verified!")

for movie in results:

    assert movie["original_language"] == "en"

print("Language filter passed!")

ACTION = 28
THRILLER = 53

for movie in results:

    genres = movie.get("genre_ids", [])

    assert ACTION in genres and THRILLER in genres

print("Genre AND filter passed!")

for movie in results:

    genres = movie.get("genre_ids", [])

    assert ACTION in genres or THRILLER in genres

print("Genre OR filter passed!")



# from tmdb_api import get_trending

# movies = get_trending()

# for movie in movies[:5]:
#     print(
#         movie.get("title"),
#         movie.get("release_date"),
#         movie.get("vote_average")
#     )

