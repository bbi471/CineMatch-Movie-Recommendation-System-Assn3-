
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
