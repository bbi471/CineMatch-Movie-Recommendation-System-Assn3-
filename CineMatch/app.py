
# app.py

import streamlit as st
import pandas as pd
import plotly.express as px

from tmdb_api import (
    tmdb_get,
    get_genres,
    get_trending,
    discover_movies,
    search_movie,
    search_person,
    get_movie_details,
    get_movie_credits,
    get_movie_keywords,
    get_movie_certification,
    get_image_url
)

from recommender import (
    recommend_movies,
    natural_language_match
)


st.set_page_config(
    page_title="CineMatch",
    page_icon="🎬",
    layout="wide"
)


# -------------------------
# SESSION STATE
# -------------------------

if "watchlist" not in st.session_state:
    st.session_state.watchlist = {}

if "comparison" not in st.session_state:
    st.session_state.comparison = []


# -------------------------
# STYLING
# -------------------------

st.markdown("""
<style>
.main {
    background-color: #101522;
}
.movie-title {
    font-size: 18px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


# -------------------------
# HEADER
# -------------------------

st.title("🎬 CineMatch")

st.caption(
    "Discover movies. Explore stories. Find your next favorite."
)


# -------------------------
# HELPER FUNCTIONS
# -------------------------

@st.cache_data(ttl=3600)
def enrich_movie(movie_id):

    details = get_movie_details(movie_id)
    credits = get_movie_credits(movie_id)
    keywords = get_movie_keywords(movie_id)

    cast = [
        x["name"]
        for x in credits.get("cast", [])[:5]
    ]

    crew = credits.get("crew", [])

    director = next(
        (
            x["name"]
            for x in crew
            if x.get("job") == "Director"
        ),
        ""
    )

    genres = [
        x["name"]
        for x in details.get("genres", [])
    ]

    return {
        "id": movie_id,
        "title": details.get("title", ""),
        "overview": details.get("overview", ""),
        "genres": genres,
        "keywords": [
            x["name"] for x in keywords
        ],
        "cast": cast,
        "director": director,
        "vote_average": details.get(
            "vote_average", 0
        ),
        "vote_count": details.get(
            "vote_count", 0
        ),
        "release_date": details.get(
            "release_date", ""
        ),
        "poster_path": details.get(
            "poster_path"
        ),
        "runtime": details.get("runtime"),
        "original_language": details.get(
            "original_language", ""
        )
    }


def show_movie_card(movie):

    col1, col2 = st.columns([1, 2])

    with col1:

        image_url = get_image_url(
            movie.get("poster_path")
        )

        if image_url:
            st.image(image_url, width=150)

    with col2:

        st.subheader(movie.get("title"))

        st.write(
            f"⭐ {movie.get('vote_average', 0):.1f}/10"
        )

        st.write(
            movie.get("release_date", "")[:4]
        )

        st.write(
            movie.get("overview", "No overview available.")
        )

        movie_id = movie["id"]

        if st.button(
            "Add to Watchlist",
            key=f"watch_{movie_id}"
        ):

            st.session_state.watchlist[
                movie_id
            ] = movie

            st.success("Movie added!")


# -------------------------
# SIDEBAR NAVIGATION
# -------------------------

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Movie Explorer",
        "Smart Recommendations",
        "My Watchlist",
        "Movie Insights",
        "Movie Comparison"
    ]
)


# -------------------------
# HOME PAGE
# -------------------------

if page == "Home":

    st.header("Trending Movies")

    movies = get_trending()

    for i in range(0, min(len(movies), 12), 4):

        cols = st.columns(4)

        for col, movie in zip(
            cols,
            movies[i:i+4]
        ):

            with col:

                image = get_image_url(
                    movie.get("poster_path")
                )

                if image:
                    st.image(image)

                st.write(
                    f"**{movie['title']}**"
                )

                st.write(
                    f"⭐ {movie['vote_average']}"
                )


# -------------------------
# MOVIE EXPLORER
# -------------------------

elif page == "Movie Explorer":

    st.header("Explore Movies")

    genres = get_genres()

    with st.sidebar:

        st.subheader("Movie Filters")

        start_year = st.number_input(
            "Start year",
            1900, 2026, 2000
        )

        end_year = st.number_input(
            "End year",
            1900, 2026, 2026
        )

        min_rating = st.slider(
            "Minimum rating",
            0.0, 10.0, 6.0
        )

        min_votes = st.number_input(
            "Minimum votes",
            0, 100000, 100
        )

        min_runtime = st.number_input(
            "Minimum runtime",
            0, 300, 60
        )

        max_runtime = st.number_input(
            "Maximum runtime",
            0, 500, 240
        )

        language = st.selectbox(
            "Language",
            ["en", "fr", "es", "ja", "ko", "zh"]
        )

        selected_genres = st.multiselect(
            "Genres",
            list(genres.keys())
        )

        genre_logic = st.radio(
            "Genre logic",
            ["AND", "OR"]
        )

        actor_name = st.text_input(
            "Actor name"
        )

        director_name = st.text_input(
            "Director name"
        )

        certification = st.selectbox(
            "US Certification",
            ["Any", "G", "PG", "PG-13", "R", "NC-17"]
        )

        search_button = st.button(
            "Search Movies",
            type="primary"
        )

    if search_button:

        if start_year > end_year:
            st.error(
                "Start year must not exceed end year."
            )

        elif min_runtime > max_runtime:
            st.error(
                "Minimum runtime must not exceed maximum runtime."
            )

        else:

            params = {
                "sort_by": "popularity.desc",
                "include_adult": "false",
                "primary_release_date.gte":
                    f"{start_year}-01-01",
                "primary_release_date.lte":
                    f"{end_year}-12-31",
                "vote_average.gte": min_rating,
                "vote_count.gte": min_votes,
                "with_runtime.gte": min_runtime,
                "with_runtime.lte": max_runtime,
                "with_original_language": language
            }

            if selected_genres:

                ids = [
                    str(genres[g])
                    for g in selected_genres
                ]

                separator = (
                    "," if genre_logic == "AND"
                    else "|"
                )

                params["with_genres"] = separator.join(
                    ids
                )

            if actor_name:

                people = search_person(actor_name)

                if people:
                    params["with_cast"] = people[0]["id"]
                else:
                    st.warning("Actor not found.")

            if director_name:

                people = search_person(director_name)

                if people:
                    params["with_crew"] = people[0]["id"]
                else:
                    st.warning("Director not found.")

            if certification != "Any":

                params["certification_country"] = "US"
                params["certification"] = certification

            try:

                results = discover_movies(params)

                st.subheader(
                    f"Found {len(results)} movies on this page"
                )

                for movie in results:
                    show_movie_card(movie)

            except Exception as error:

                st.error(
                    f"Unable to retrieve movies: {error}"
                )


# -------------------------
# SMART RECOMMENDATIONS
# -------------------------

elif page == "Smart Recommendations":

    st.header("Smart Movie Recommendations")

    st.write(
        "Describe the movie you want to watch."
    )

    query = st.text_area(
        "Natural language search",
        placeholder=(
            "I want an exciting science fiction "
            "movie about space exploration."
        )
    )

    if st.button("Find Recommendations"):

        if not query.strip():

            st.warning("Please enter a description.")

        else:

            candidates = []

            # Discover a broad set of movies.
            data = discover_movies({
                "sort_by": "popularity.desc",
                "vote_count.gte": 100,
                "vote_average.gte": 5
            })

            # Enrich the movies with plot, cast,
            # keywords, and director information.
            progress = st.progress(0)

            for index, movie in enumerate(data):

                try:
                    candidates.append(
                        enrich_movie(movie["id"])
                    )
                except Exception:
                    continue

                progress.progress(
                    (index + 1) / max(len(data), 1)
                )

            results = natural_language_match(
                query,
                candidates,
                top_n=10
            )

            st.subheader("Recommended Movies")

            for result in results:

                movie = result["movie"]

                st.write(
                    f"### {movie['title']}"
                )

                st.write(
                    f"Match score: {result['score']:.2%}"
                )

                st.write(
                    movie["overview"]
                )


# -------------------------
# WATCHLIST
# -------------------------

elif page == "My Watchlist":

    st.header("My Watchlist")

    watchlist = st.session_state.watchlist

    if not watchlist:

        st.info(
            "Your watchlist is empty. "
            "Add movies from Home or Movie Explorer."
        )

    else:

        for movie_id, movie in list(watchlist.items()):

            show_movie_card(movie)

            if st.button(
                "Remove",
                key=f"remove_{movie_id}"
            ):

                del st.session_state.watchlist[
                    movie_id
                ]

                st.rerun()


# -------------------------
# MOVIE INSIGHTS
# -------------------------

elif page == "Movie Insights":

    st.header("Movie Data Insights")

    movies = get_trending()

    df = pd.DataFrame(movies)

    if not df.empty:

        df["release_year"] = pd.to_datetime(
            df["release_date"],
            errors="coerce"
        ).dt.year

        st.metric(
            "Movies Retrieved",
            len(df)
        )

        st.metric(
            "Average Rating",
            round(df["vote_average"].mean(), 2)
        )

        fig = px.histogram(
            df,
            x="vote_average",
            nbins=10,
            title="Distribution of Movie Ratings"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        yearly = (
            df.dropna(subset=["release_year"])
            .groupby("release_year")
            .size()
            .reset_index(name="movie_count")
        )

        fig2 = px.bar(
            yearly,
            x="release_year",
            y="movie_count",
            title="Trending Movies by Release Year"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )


# -------------------------
# MOVIE COMPARISON
# -------------------------

elif page == "Movie Comparison":

    st.header("Compare Movies")

    title1 = st.text_input(
        "First movie title"
    )

    title2 = st.text_input(
        "Second movie title"
    )

    if st.button("Compare Movies"):

        if not title1.strip() or not title2.strip():

            st.warning("Enter two movie titles.")

        else:

            result1 = search_movie(title1)
            result2 = search_movie(title2)

            if result1 and result2:

                movie1 = get_movie_details(
                    result1[0]["id"]
                )

                movie2 = get_movie_details(
                    result2[0]["id"]
                )

                comparison = pd.DataFrame({
                    movie1["title"]: [
                        movie1.get("vote_average"),
                        movie1.get("runtime"),
                        movie1.get("vote_count")
                    ],
                    movie2["title"]: [
                        movie2.get("vote_average"),
                        movie2.get("runtime"),
                        movie2.get("vote_count")
                    ]
                }, index=[
                    "Rating",
                    "Runtime (minutes)",
                    "Vote Count"
                ])

                st.dataframe(
                    comparison,
                    use_container_width=True
                )

            else:

                st.error(
                    "One or both movies were not found."
                )
