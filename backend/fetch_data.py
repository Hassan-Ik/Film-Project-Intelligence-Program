import os, requests, re
from typing import List, Dict, Any
from dotenv import load_dotenv
load_dotenv()
import time

OMDB_API_KEY = os.getenv("OMDB_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def normalize_title(title: str) -> str:
    """Normalize a movie title for matching by removing special characters and converting to lowercase."""
    if not title:
        return ""
    return re.sub(r'[^a-z0-9 ]', '', title.lower())

def search_omdb_movies_by_titles(titles: List[str], top_n: int = 5) -> List[Dict]:
    """Search OMDb for movies using exact title matches, retrieving detailed metadata."""
    if not OMDB_API_KEY:
        print("OMDb API key missing.")
        return []

    results = []
    for title in titles[:top_n]:  # Limit to top_n titles to respect API rate limits
        if not title.strip():
            continue
        try:
            url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}&type=movie&plot=full"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("Response") == "True" and data.get("imdbID"):
                    results.append({
                        "source": "OMDb",
                        "Title": data.get("Title"),
                        "Year": data.get("Year", "0")[:4],
                        "Genre": data.get("Genre", ""),
                        "Plot": data.get("Plot", ""),
                        "Director": data.get("Director", ""),
                        "Actors": data.get("Actors", ""),
                        "imdbRating": data.get("imdbRating", ""),
                        "imdbVotes": data.get("imdbVotes", ""),
                        "Metascore": data.get("Metascore", ""),
                        "Poster_Path": data.get("Poster", "")
                    })
            time.sleep(0.2)  # Respect OMDb rate limits
        except Exception as e:
            print(f"OMDb search error for title '{title}': {e}")
            continue

    return results

def search_tmdb_movies_by_titles(titles: List[str], top_n: int = 5) -> List[Dict]:
    """Search TMDb for movies using exact title matches, retrieving detailed metadata."""
    if not TMDB_API_KEY:
        print("TMDb API key missing.")
        return []

    results = []
    base_url = "https://api.themoviedb.org/3"

    for title in titles[:top_n]:  # Limit to top_n titles for API efficiency
        if not title.strip():
            continue
        try:
            search_url = f"{base_url}/search/movie"
            params = {
                "api_key": TMDB_API_KEY,
                "query": title,
                "language": "en-US",
                "page": 1
            }
            response = requests.get(search_url, params=params, timeout=5)
            if response.status_code == 200:
                search_data = response.json()
                movies = search_data.get("results", [])
                for movie in movies[:1]:  # Take first result if title matches
                    if movie.get("id") and normalize_title(movie.get("title", "")) == normalize_title(title):
                        detail_url = f"{base_url}/movie/{movie['id']}"
                        detail_params = {
                            "api_key": TMDB_API_KEY,
                            "language": "en-US",
                            "append_to_response": "keywords,credits"
                        }
                        detail_response = requests.get(detail_url, params=detail_params, timeout=5)
                        if detail_response.status_code == 200:
                            detail_data = detail_response.json()
                            results.append({
                                "source": "TMDb",
                                "Title": detail_data.get("title", ""),
                                "Year": detail_data.get("release_date", "0")[:4],
                                "Genres": [g["name"] for g in detail_data.get("genres", [])],
                                "Overview": detail_data.get("overview", ""),
                                "Keywords": [k["name"] for k in detail_data.get("keywords", {}).get("keywords", [])],
                                "Cast": [c["name"] for c in detail_data.get("credits", {}).get("cast", [])[:3]],
                                "Director": next((c["name"] for c in detail_data.get("credits", {}).get("crew", []) if c["job"] == "Director"), ""),
                                "Popularity": detail_data.get("popularity", ""),
                                "VoteAverage": detail_data.get("vote_average", ""),
                                "VoteCount": detail_data.get("vote_count", ""),
                                "Budget": detail_data.get("budget", 0),
                                "Revenue": detail_data.get("revenue", 0),
                                "Poster_Path": detail_data.get("poster_path", "")
                            })
            time.sleep(0.3)  # Respect TMDb rate limits
        except Exception as e:
            print(f"TMDb search error for title '{title}': {e}")
            continue

    return results

def merge_tmdb_omdb_titles(tmdb_results: List[Dict], omdb_results: List[Dict], top_n: int = 5) -> List[Dict]:
    """
    Merge TMDb and OMDb results, prioritizing TMDb for budget/revenue, filling gaps with OMDb.
    Deduplicate by normalized title, sort by release date (ascending), and return detailed metadata.
    """
    merged_results = {}
    
    # Process TMDb results (preferred source for budget/revenue)
    for movie in tmdb_results:
        title = movie.get("Title")
        year = movie.get("Year", "0")
        if title and year and year.isdigit():
            normalized = normalize_title(title)
            merged_results[normalized] = {
                "Title": title,
                "Year": int(year),
                "Genres": movie.get("Genres", []),
                "Overview": movie.get("Overview", ""),
                "Keywords": movie.get("Keywords", []),
                "Cast": movie.get("Cast", []),
                "Director": movie.get("Director", ""),
                "Popularity": movie.get("Popularity", ""),
                "VoteAverage": movie.get("VoteAverage", ""),
                "VoteCount": movie.get("VoteCount", ""),
                "Budget": movie.get("Budget", 0),
                "Revenue": movie.get("Revenue", 0),
                "source": "TMDb",
                "Poster_Path": movie.get("Poster_Path", None)
            }

    # Add OMDb results for missing titles or fields
    for movie in omdb_results:
        title = movie.get("Title")
        year = movie.get("Year", "0")
        if title and year and year.isdigit():
            normalized = normalize_title(title)
            if normalized not in merged_results:
                merged_results[normalized] = {
                    "Title": title,
                    "Year": int(year),
                    "Genres": movie.get("Genre", "").split(", ") if movie.get("Genre") else [],
                    "Overview": movie.get("Plot", ""),
                    "Keywords": [],  # OMDb doesn't provide keywords
                    "Cast": movie.get("Actors", "").split(", ") if movie.get("Actors") else [],
                    "Director": movie.get("Director", ""),
                    "Popularity": "",  # OMDb doesn't provide popularity
                    "VoteAverage": movie.get("imdbRating", ""),
                    "VoteCount": movie.get("imdbVotes", ""),
                    "Budget": 0,  # OMDb doesn't provide budget
                    "Revenue": 0,  # OMDb doesn't provide revenue
                    "source": "OMDb",
                    "Poster_Path": movie.get("Poster_Path", None)
                }
            else:
                # Fill missing TMDb fields with OMDb data
                existing = merged_results[normalized]
                if not existing["Overview"] and movie.get("Plot"):
                    existing["Overview"] = movie.get("Plot")
                if not existing["Genres"] and movie.get("Genre"):
                    existing["Genres"] = movie.get("Genre").split(", ")
                if not existing["Cast"] and movie.get("Actors"):
                    existing["Cast"] = movie.get("Actors").split(", ")
                if not existing["Director"] and movie.get("Director"):
                    existing["Director"] = movie.get("Director")
                if not existing["VoteAverage"] and movie.get("imdbRating"):
                    existing["VoteAverage"] = movie.get("imdbRating")
                if not existing["VoteCount"] and movie.get("imdbVotes"):
                    existing["VoteCount"] = movie.get("imdbVotes")

    # Convert to list and sort by year (ascending)
    result_list = sorted(
        merged_results.values(),
        key=lambda x: x["Year"]
    )

    return result_list[:top_n]