import os, requests, re
from typing import List, Dict, Any
from dotenv import load_dotenv
load_dotenv()
import time

OMDB_API_KEY = os.getenv("OMDB_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def fetch_omdb_data(title: str) -> dict:
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return {}
    data = resp.json()
    if data.get("Response") == "False":
        return {}
    return {
        "title": data.get("Title"),
        "year": data.get("Year"),
        "genre": data.get("Genre"),
        "plot": data.get("Plot"),
        "director": data.get("Director"),
        "actors": data.get("Actors"),
        "ratings": data.get("Ratings")
    }

def fetch_tmdb_data(title: str) -> dict:
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
    search_resp = requests.get(search_url).json()
    results = search_resp.get("results")
    if not results:
        return {}
    movie_id = results[0]["id"]
    details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=credits,keywords"
    details_resp = requests.get(details_url).json()
    return {
        "title": details_resp.get("title"),
        "overview": details_resp.get("overview"),
        "genres": [g["name"] for g in details_resp.get("genres", [])],
        "keywords": [k["name"] for k in details_resp.get("keywords", {}).get("keywords", [])],
        "cast": [c["name"] for c in details_resp.get("credits", {}).get("cast", [])[:5]],
        "crew": [c["name"] for c in details_resp.get("credits", {}).get("crew", [])[:5]],
        "release_date": details_resp.get("release_date")
    }

def search_omdb_movies(keywords: List[str]) -> List[Dict]:
    """Search OMDb for movies using plot/genre-focused keywords."""
    if not OMDB_API_KEY:
        return []

    results = []
    for keyword in keywords[:5]:  # Allow more keywords for better coverage
        try:
            url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={keyword}&type=movie"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                search_data = response.json()
                if search_data.get("Response") == "True":
                    for movie in search_data.get("Search", []):
                        if movie.get("imdbID"):
                            # Get full details
                            detail_url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={movie['imdbID']}&plot=full"
                            detail_response = requests.get(detail_url, timeout=5)
                            if detail_response.status_code == 200:
                                full_data = detail_response.json()
                                if full_data.get("Response") == "True":
                                    results.append({
                                        "source": "OMDb",
                                        "Title": full_data.get("Title"),
                                        "Year": full_data.get("Year"),
                                        "Genre": full_data.get("Genre"),
                                        "Plot": full_data.get("Plot"),
                                        "Director": full_data.get("Director"),
                                        "Actors": full_data.get("Actors"),
                                        "imdbRating": full_data.get("imdbRating"),
                                        "imdbVotes": full_data.get("imdbVotes"),
                                        "Metascore": full_data.get("Metascore")
                                    })
            time.sleep(0.2)
        except Exception as e:
            print(f"OMDb search error for '{keyword}': {e}")
            continue

    return results[:5]  # Return top 5 matches

def search_tmdb_movies(keywords: List[str]) -> List[Dict]:
    """Search TMDb for movies using plot/genre-focused keywords."""
    if not TMDB_API_KEY:
        return []

    results = []
    base_url = "https://api.themoviedb.org/3"

    for keyword in keywords[:5]:
        try:
            search_url = f"{base_url}/search/movie"
            params = {
                "api_key": TMDB_API_KEY,
                "query": keyword,
                "language": "en-US",
                "page": 1
            }
            response = requests.get(search_url, params=params, timeout=5)
            if response.status_code == 200:
                search_data = response.json()
                movies = search_data.get("results", [])
                for movie in movies[:2]:
                    if movie.get("id"):
                        detail_url = f"{base_url}/movie/{movie['id']}"
                        detail_params = {
                            "api_key": TMDB_API_KEY,
                            "language": "en-US",
                            "append_to_response": "keywords,credits"
                        }
                        detail_response = requests.get(detail_url, params=detail_params, timeout=5)
                        if detail_response.status_code == 200:
                            detail_data = detail_response.json()
                            keywords_list = [k["name"] for k in detail_data.get("keywords", {}).get("keywords", [])]
                            cast_list = [c["name"] for c in detail_data.get("credits", {}).get("cast", [])[:3]]
                            results.append({
                                "source": "TMDb",
                                "Title": detail_data.get("title"),
                                "ReleaseDate": detail_data.get("release_date"),
                                "Genres": [g["name"] for g in detail_data.get("genres", [])],
                                "Overview": detail_data.get("overview"),
                                "Keywords": keywords_list,
                                "Cast": cast_list,
                                "Popularity": detail_data.get("popularity"),
                                "VoteAverage": detail_data.get("vote_average"),
                                "VoteCount": detail_data.get("vote_count"),
                                "Budget": detail_data.get("budget"),
                                "Revenue": detail_data.get("revenue")
                            })
            time.sleep(0.3)
        except Exception as e:
            print(f"TMDb search error for '{keyword}': {e}")
            continue

    return results[:5]

def normalize_title(title: str) -> str:
    if not title:
        return ""
    return re.sub(r'[^a-z0-9 ]', '', title.lower())

def merge_tmdb_omdb(tmdb_results: List[Dict], omdb_results: List[Dict], top_n: int = 5) -> List[Dict]:
    """
    Merge TMDb with OMDb.
    - TMDb is the main source (budget/revenue),
    - OMDb fills missing fields if TMDb has none.
    - If TMDb has no results, return OMDb results with empty Budget/Revenue.
    - Return top N results based on Revenue (high to low) and then ReleaseDate (latest first).
    """
    if not tmdb_results:
        # Add empty Budget/Revenue to OMDb results
        for m in omdb_results:
            m.setdefault("Budget", None)
            m.setdefault("Revenue", None)
        # Sort OMDb results by ReleaseDate and Revenue
        sorted_results = sorted(
            omdb_results, 
            key=lambda x: (
                int(x.get("Revenue", 0) or 0),
                x.get("Year", "0")
            ), 
            reverse=True
        )
        return sorted_results[:top_n]

    merged_results = []
    # Build OMDb index by normalized title + year
    omdb_index = {(normalize_title(m.get("Title", "")), m.get("Year", "")[:4]): m for m in omdb_results}

    for tmdb in tmdb_results:
        title = normalize_title(tmdb.get("Title", ""))
        year = tmdb.get("ReleaseDate", "")[:4] if tmdb.get("ReleaseDate") else ""

        merged = tmdb.copy()
        # Fill missing fields from OMDb
        omdb_match = omdb_index.get((title, year))
        if omdb_match:
            for k, v in omdb_match.items():
                if k not in merged or not merged[k]:
                    merged[k] = v
        merged_results.append(merged)

    # Sort by Revenue (desc) then ReleaseDate (desc)
    sorted_results = sorted(
        merged_results, 
        key=lambda x: (
            int(x.get("Revenue", 0) or 0), 
            x.get("ReleaseDate", "0")
        ), 
        reverse=True
    )

    return sorted_results[:top_n]

