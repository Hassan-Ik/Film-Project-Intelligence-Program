from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from openai import OpenAI, OpenAIError, AsyncOpenAI
import os
import json
import numpy as np
from transformers import pipeline
from models import AnalysisResponse, StoryRequest, EmotionalArcPoint, Character, StoryImpactReport
from utils import *
from dotenv import load_dotenv
from fetch_data import *

load_dotenv()

# Validate environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Hugging Face pipelines (configurable models)
NER_MODEL = os.getenv("NER_MODEL", "dslim/bert-base-NER")
EMOTION_MODEL = os.getenv("EMOTION_MODEL", "j-hartmann/emotion-english-distilroberta-base")
ner = pipeline("ner", model=NER_MODEL, aggregation_strategy="simple")
emotion_model = pipeline(
    "text-classification",
    model=EMOTION_MODEL,
    return_all_scores=True
)

def extract_keywords(synopsis: str) -> List[str]:
    """
    Extract keywords suitable for TMDb/OMDb search, focusing on plot, genre, and main concepts.
    Ensures the output is always a valid JSON array of strings.
    """
    prompt = f"""
    Extract 3-6 keywords, phrases, or proper nouns from this movie synopsis
    that would help find it in a movie database (TMDb or OMDb). 
    Focus primarily on:
    - Main plot points or story concepts
    - Key genres or themes
    - Important characters or locations only if central to the plot
    
    Avoid emphasizing actors or directors.
    
    Return ONLY a JSON array of strings. No explanations, no extra text.
    Synopsis:
    {synopsis}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        # Remove any code block formatting
        if content.startswith("```"):
            content = content.strip("`").replace("json", "").strip()

        # Parse JSON safely
        keywords = json.loads(content)
        if isinstance(keywords, list):
            # Keep only strings and remove duplicates
            return list(dict.fromkeys([k for k in keywords if isinstance(k, str) and len(k) > 1]))
        else:
            print("Unexpected format, got:", type(keywords))
            return []

    except json.JSONDecodeError as e:
        print("JSON decode error:", e)
        print("Raw content:", content)  # debug
        return []
    except Exception as e:
        print("Error extracting keywords:", e)
        return []



# To fetch movies from omdb and tmdb api call and build market context
def build_market_context(synopsis: str) -> str:
    """Build market context string from TMDb (main) + OMDb (fallback) results."""
    keywords = extract_keywords(synopsis)
    if not keywords:
        return ""

    print(f"Extracted keywords for market analysis: {keywords}")

    # Search both APIs
    tmdb_results = search_tmdb_movies(keywords)
    omdb_results = search_omdb_movies(keywords)

    # Merge (TMDb main + OMDb fallback fields)
    all_results = merge_tmdb_omdb(tmdb_results, omdb_results)

    print(f"Found {len(all_results)} comparable movies")

    if not all_results:
        return ""

    # Format results for GPT prompt
    context = "MARKET CONTEXT - Comparable Movies:\n\n"

    for i, movie in enumerate(all_results[:5], 1):
        context += f"MOVIE {i}: {movie.get('Title', 'Unknown')}\n"
        context += f"Year: {movie.get('Year') or movie.get('ReleaseDate', 'N/A')}\n"

        if movie.get("Genres"):
            context += f"Genres: {', '.join(movie['Genres'])}\n"
        elif movie.get("Genre"):
            context += f"Genres: {movie['Genre']}\n"

        if movie.get("Director"):
            context += f"Director: {movie['Director']}\n"

        if movie.get("Cast"):
            context += f"Cast: {', '.join(movie['Cast'])}\n"
        elif movie.get("Actors"):
            context += f"Cast: {movie['Actors']}\n"

        if movie.get("imdbRating"):
            context += f"IMDB Rating: {movie['imdbRating']}\n"
        if movie.get("VoteAverage"):
            context += f"TMDb Rating: {movie['VoteAverage']}\n"

        if movie.get("Popularity"):
            context += f"Popularity: {movie['Popularity']}\n"

        if movie.get("Metascore"):
            context += f"Metascore: {movie['Metascore']}\n"

        if movie.get("Keywords"):
            context += f"Keywords: {', '.join(movie['Keywords'][:5])}\n"

        if movie.get("Overview"):
            context += f"Overview: {movie['Overview'][:300]}...\n"
        elif movie.get("Plot"):
            context += f"Plot: {movie['Plot'][:300]}...\n"

        if movie.get("Budget"):
            context += f"Budget: {movie['Budget']}\n"
          
        if movie.get("Revenue"):
            context += f"Budget: {movie['Budget']}\n"
            
        context += "\n"

    context += (
        "Use this market data to assess the synopsis's commercial potential, "
        "genre fit, and audience appeal compared to successful films.\n\n"
    )

    return context


# ---------------------------------------------------------------
# First Endpoint
# Analyze synopsis not more than 8 pages
# ---------------------------------------------------------------
@app.post("/analyze_synopsis")
def analyze_synopsis(req: StoryRequest):
    """
    Analyze a movie synopsis for creative and commercial potential.
    """
    try:
        if not req.story.strip():
            raise HTTPException(status_code=400, detail="Synopsis cannot be empty")

        print("Here")
        
        # Build market context from OMDb/TMDb
        market_context = build_market_context(req.story)

        # A clear and robust openai script for good JSON based response
        prompt = f"""
        You are an expert Hollywood script and story analyst and data scientist. Analyze the following film synopsis and provide ONLY a valid JSON response with data-driven insights about its creative potential and commercial viability.

        SYNOPSIS: {req.story}
        {market_context if market_context else "Note: Limited market data available - base analysis on general industry trends."}

        Analyze this synopsis considering:
        1. How the story's genre, themes, and structure compare to successful films
        2. Current market trends and audience preferences in similar categories
        3. Commercial potential based on comparable movies' performance
        4. Casting and production feasibility based on similar projects

        Return ONLY a single JSON object with this exact structure. Do not include markdown, explanations, or additional text.

        {{
            "story_impact_report": {{
                "title": "Professional Report Title - {req.story[:30]}...",
                "logline": "A compelling, single-sentence logline summarizing the story's core conflict and stakes",
                "top_level_score": {{
                    "overall": 85,
                    "narrative_strength": 78,
                    "market_fit": 92
                }},
                "emotional_arc_data": [
                    {{"point": "Beginning", "intensity": 2}},
                    {{"point": "End of Act I", "intensity": 6}},
                    {{"point": "Midpoint", "intensity": -4}},
                    {{"point": "All is Lost Moment", "intensity": -8}},
                    {{"point": "Climax", "intensity": 10}},
                    {{"point": "End", "intensity": 7}}
                ],
                "key_insights": {{
                    "summary": "A professional 2-3 sentence analysis of the story's core narrative strengths and market appeal.",
                    "genres": ["Drama", "Thriller", "Sci-Fi"],
                    "themes": ["Redemption", "Technology", "Family"],
                    "target_audience": ["Millennials", "Sci-Fi Fans", "Urban Professionals"]
                }},
                "characters": [
                    {{
                        "role": "Protagonist",
                        "description_short": "A brief description of their personality, goals, and arc.",
                        "attributes": {{
                            "archetype": "Reluctant Hero",
                            "audience_appeal_score": 8,
                            "comparable_actors": ["Ryan Gosling", "Tom Hardy", "Oscar Isaac"]
                        }}
                    }}
                ],
                "pitch_ready_copy": {{
                    "key_pitch_points": [
                        "High-concept premise with universal emotional stakes",
                        "Relatable protagonist with clear character arc", 
                        "Timely themes that resonate with current audiences"
                    ],
                    "one_liner": "A catchy tagline that captures the film's essence"
                }}
            }}
        }}

        IMPORTANT: Return ONLY the JSON object above with real data for this specific synopsis. Ensure all values are valid JSON (use double quotes, no trailing commas).
        """

        # Using the OpenAI client
        try:
          response = client.chat.completions.create(
              model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
              messages=[
                  {
                      "role": "system", 
                      "content": "You are a precise JSON generator and Hollywood market analyst. Always respond with valid JSON only, incorporating market data and competitive insights. No explanations or additional text."
                  },
                  {"role": "user", "content": prompt}
              ],
              temperature=0.45,
              max_tokens=3000
          )

          content = response.choices[0].message.content.strip()
        except OpenAIError as e:
            print("Error processing synopsis due to openai error")
            print(e)
            raise HTTPException(status_code=500)
        
        print("OpenAI Generated content is")
        print(content)

        if not content:
            raise HTTPException(status_code=500, detail="Empty response from OpenAI")
        try:
            content = content.strip()
            if content.startswith("```json"):
                content = content.replace("```json")
            if content.startswith("```"):
                content = content.replace("```", "").strip()
            
            parsed = json.loads(content)
            
            if "story_impact_report" not in parsed:
                raise ValueError("Missing 'story_impact_report' key in response")
            
            # Add market context to response for transparency (optional)
            result = parsed["story_impact_report"]
            
            if market_context:
                result["metadata"] = {
                    "market_search_performed": True,
                    "comparable_movies_found": len(extract_keywords(req.story)),
                    "analysis_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                result["metadata"] = {
                    "market_search_performed": False,
                    "reason": "API keys not configured"
                }

            return result
            
        except json.JSONDecodeError as json_err:
            print(f"JSON Parse Error: {json_err}")
            print(f"Raw response: {content[:500]}...")  # First 500 chars for debugging
            
            raise HTTPException(
                status_code=500, 
                detail="Failed to parse analysis - please try again with a different synopsis"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        # Log the full error for debugging
        print(f"Unexpected error in analyze_synopsis: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis failed: {str(e) if os.getenv('DEBUG') else 'Internal server error'}"
        )

# Todo: Needs work on this, its for full script
# Character Analysis with NER
def analyze_characters(story: str) -> List[Dict[str, str]]:
    """Extract and analyze characters using NER and screenplay parsing."""
    # Extract names from dialogue cues
    names = extract_character_names(story)
    
    # Supplement with NER for short scripts or process chunks for long scripts
    chunks = chunk_text(story, max_length=10000)
    ner_names = set()
    for chunk in chunks:
        results = ner(chunk)
        ner_names.update([r["word"] for r in results if r["entity_group"] == "PER"])
    
    # Combine and limit to top 5 names
    all_names = list(dict.fromkeys(names + list(ner_names)))[:5]
    if not all_names:
        return []

    # Analyze characters with GPT
    prompt = f"""
    You are a Hollywood story analyst. Assign roles and archetypes to these characters
    based on the story context. Output as JSON list of objects with fields:
    name, role, archetype, description.

    Characters: {all_names}

    Story (excerpt for context):
    {story[:10000]}  # Use full story for short scripts, first 10,000 chars for long
    """
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        return json.loads(response.choices[0].message.content)
    except OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response from OpenAI: {str(e)}")

# Story Structure Analysis
def analyze_story_structure(story: str, is_short: bool) -> Dict[str, Any]:
    """
    Analyze screenplay for narrative beats and characters using a single GPT call.
    
    Args:
        story: The input screenplay text.
        is_short: True if script is 3–4 pages, False for longer scripts.
        
    Returns:
        Dictionary with 'beats' (object) and 'characters' (list).
    """
    # Extract character names for initial filtering
    initial_names = extract_character_names(story)[:5]
    
    # Adjust prompt based on script length
    if is_short:
        prompt = f"""
        You are a professional Hollywood script analyst. Analyze this short screenplay (3–4 pages).
        Tasks:
        1. Identify narrative beats (Beginning, Middle, End). For each, provide 1–2 paragraphs of the story text.
        2. Assign roles and archetypes to these characters: {initial_names}.
           Output as a JSON list of objects with fields: name, role, archetype, description.
        Return a JSON object with 'beats' (object) and 'characters' (list).

        Screenplay:
        {story}
        """
    else:
        # Chunk for long scripts
        chunks = chunk_text(story, max_length=20000)
        beats = {}
        characters = []
        for i, chunk in enumerate(chunks):
            prompt = f"""
            You are a professional Hollywood script analyst. Analyze screenplay chunk ({i+1}/{len(chunks)}).
            Tasks:
            1. Identify narrative beats (Beginning, End of Act I, Midpoint, All is Lost Moment, Climax, End).
               For each, provide 2–4 paragraphs of the story text.
            2. Assign roles and archetypes to these characters: {initial_names}.
               Output as a JSON list of objects with fields: name, role, archetype, description.
            Return a JSON object with 'beats' (object) and 'characters' (list).

            Screenplay chunk:
            {chunk}
            """
            try:
                response = client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.4
                )
                result = json.loads(response.choices[0].message.content)
                beats.update(result.get("beats", {}))
                if result.get("characters"):
                    existing_names = {c["name"] for c in characters}
                    for c in result["characters"]:
                        if c["name"] not in existing_names:
                            characters.append(c)
            except OpenAIError as e:
                raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
            except json.JSONDecodeError as e:
                raise HTTPException(status_code=500, detail=f"Invalid JSON response from OpenAI: {str(e)}")
        return {"beats": beats, "characters": characters[:5]}
    
    # Single call for short scripts
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        return json.loads(response.choices[0].message.content)
    except OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response from OpenAI: {str(e)}")

# -------------------------------------------------------------------------------
# Second Endpoint
# Analyze full script or story
# --------------------------------------------------------------------------------
@app.post("/analyze", response_model=AnalysisResponse)
def analyze_story(req: StoryRequest):
    """
    Analyze a screenplay for narrative beats, emotional arc, characters, and metadata.
    
    Args:
        req: StoryRequest object containing the screenplay text.
        
    Returns:
        AnalysisResponse with emotional arc, characters, story score, tags, and audience.
    """
    try:
        # Validate input
        if not req.story.strip():
            raise HTTPException(status_code=400, detail="Screenplay cannot be empty")
        if len(req.story) < 100:
            raise HTTPException(status_code=400, detail="Screenplay too short (minimum 100 characters)")
        if len(req.story) > 500000:  # ~250 pages
            raise HTTPException(status_code=400, detail="Screenplay exceeds maximum length")

        # Determine if script is short (3–4 pages, ~800 words or ~6000 chars)
        is_short = len(req.story) <= 6000

        # Separate dialogue and action
        dialogue, action = separate_dialogue_action(req.story)

        # 1. Story structure and character analysis
        structure = analyze_story_structure(req.story, is_short)
        beats = structure["beats"]
        characters = [Character(**c) for c in structure["characters"]]

        # 2. Emotional arc (use dialogue for short scripts, beats for long)
        emotional_arc = []
        if is_short:
            scores = emotion_model(dialogue or req.story[:5000])[0]
            valence, arousal = valence_arousal(scores)
            emotional_arc.append(EmotionalArcPoint(point="Overall", valence=valence, arousal=arousal))
        else:
            for point, text in beats.items():
                scores = emotion_model(dialogue[:5000] if point in ["Beginning", "End of Act I"] else text)[0]
                valence, arousal = valence_arousal(scores)
                emotional_arc.append(EmotionalArcPoint(point=point, valence=valence, arousal=arousal))

        # 3. Story-level scoring
        weights = {"Climax": 2.0, "All is Lost Moment": 1.5, "Midpoint": 1.2, "Beginning": 1.0, "End of Act I": 1.0, "End": 1.0, "Overall": 1.0}
        story_score = int(np.sum([weights.get(e.point, 1.0) * (abs(e.valence) + abs(e.arousal)) for e in emotional_arc]) * 2)

        # 4. Tags & audience
        prompt = f"""
        Analyze the following screenplay. Suggest 3 genres, 3 themes, and 3 target audiences.
        Return as JSON:
        {{
          "tags": ["", "", ""],
          "audience": ["", "", ""]
        }}

        Screenplay (excerpt):
        {req.story[:10000]}  # Use full story for short scripts, first 10,000 chars for long
        """
        try:
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            extra = json.loads(response.choices[0].message.content)
        except OpenAIError as e:
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Invalid JSON response from OpenAI: {str(e)}")

        return AnalysisResponse(
            emotional_arc=emotional_arc,
            characters=characters,
            story_score=story_score,
            tags=extra["tags"],
            audience=extra["audience"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
