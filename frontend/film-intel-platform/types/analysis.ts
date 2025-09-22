export interface EmotionalArcPoint {
  point: string;
  intensity: number;
}

export interface Character {
  name: string;
  role: string;
  archetype: string;
}

export interface AnalysisResponse {
  emotional_arc: EmotionalArcPoint[];
  characters: Character[];
  story_score: number;
  tags: string[];
  audience: string[];
}
