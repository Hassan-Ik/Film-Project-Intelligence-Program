# backend/models.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class StoryRequest(BaseModel):
    story: str

class EmotionalArcPoint(BaseModel):
    point: str
    valence: int
    arousal: int

# class Character(BaseModel):
#     name: str
#     role: str
#     archetype: str
#     description: str


class CharacterAttributes(BaseModel):
    archetype: str
    audience_appeal_score: int = Field(..., ge=-10, le=10)
    comparable_actors: List[str]

class Character(BaseModel):
    name: str
    role: str
    description_short: str
    attributes: CharacterAttributes

class AnalysisResponse(BaseModel):
    emotional_arc: List[EmotionalArcPoint]
    characters: List[Character]
    story_score: int
    tags: List[str]
    audience: List[str]

class StoryImpactReport(BaseModel):
    title: str
    logline: str
    top_level_score: Dict[str, int]
    emotional_arc_data: list[EmotionalArcPoint]
    key_insights: Dict[str, Any]
    characters: list[Character]
    pitch_ready_copy: Dict[str, Any]