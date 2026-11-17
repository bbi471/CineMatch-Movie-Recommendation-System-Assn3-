
import requests
import streamlit as st

# TMDB API base URL
BASE_URL = "https://api.themoviedb.org/3"

# Retrieve your API Read Access Token
TOKEN = st.secrets["TMDB_ACCESS_TOKEN"]

# Authentication headers
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "accept": "application/json"
}

# Test the connection
url = f"{BASE_URL}/movie/popular"

response = requests.get(
    url,
    headers=headers,
    params={"language": "en-US", "page": 1},
    timeout=20
)

# Check the response
print("HTTP Status Code:", response.status_code)

if response.status_code == 200:

    data = response.json()

    print("TMDB connection successful!")

    print("Total Results:", data["total_results"])

    for movie in data["results"][:5]:

        print(
            movie["title"],
            movie.get("release_date"),
            movie.get("vote_average")
        )

else:

    print("API request failed:")
    print(response.text)
