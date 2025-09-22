import os, requests
import re
from utils import chunk_text
from dotenv import load_dotenv
load_dotenv()

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
    """Search OMDb for similar movies using extracted keywords."""
    if not OMDb_API_KEY:
        return []
    
    results = []
    for keyword in keywords[:3]:  # Limit to top 3 keywords
        try:
            url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={keyword}&type=movie"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("Response") == "True" and data.get("imdbID"):
                    # Get full details
                    detail_url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={data['imdbID']}&plot=short"
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
                    time.sleep(0.2)  # Rate limiting
            time.sleep(0.2)
        except Exception as e:
            print(f"OMDb search error for '{keyword}': {e}")
            continue
    
    return results[:3]  # Return top 3 matches

def search_tmdb_movies(keywords: List[str]) -> List[Dict]:
    """Search TMDb for similar movies using extracted keywords."""
    if not TMDB_API_KEY:
        return []
    
    results = []
    base_url = "https://api.themoviedb.org/3"
    
    for keyword in keywords[:3]:  # Limit to top 3 keywords
        try:
            # Search movies
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
                
                for movie in movies[:2]:  # Get top 2 results per keyword
                    if movie.get("id"):
                        # Get movie details
                        detail_url = f"{base_url}/movie/{movie['id']}"
                        detail_params = {
                            "api_key": TMDB_API_KEY,
                            "language": "en-US",
                            "append_to_response": "keywords,credits"
                        }
                        detail_response = requests.get(detail_url, params=detail_params, timeout=5)
                        
                        if detail_response.status_code == 200:
                            detail_data = detail_response.json()
                            
                            # Get keywords
                            keywords_data = detail_data.get("keywords", {}).get("keywords", [])
                            keywords_list = [k["name"] for k in keywords_data[:5]]
                            
                            # Get cast (top 3)
                            cast_data = detail_data.get("credits", {}).get("cast", [])
                            cast_list = [c["name"] for c in cast_data[:3]]
                            
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
                                "VoteCount": detail_data.get("vote_count")
                            })
                            
            time.sleep(0.2)  # Rate limiting
        except Exception as e:
            print(f"TMDb search error for '{keyword}': {e}")
            continue
    
    return results[:3]