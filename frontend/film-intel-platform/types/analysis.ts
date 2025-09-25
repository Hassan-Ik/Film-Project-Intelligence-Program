export interface EmotionalArcPoint {
  point: string;
  intensity: number;
}

export interface CharacterAttributes {
  archetype: string;
  audience_appeal_score: number;
  comparable_actors: string[];
}

export interface Character {
  role: string;
  description_short: string;
  attributes: CharacterAttributes;
}

export interface TopLevelScore {
  overall: number;
  narrative_strength: number;
  market_fit: number;
}

export interface KeyInsights {
  summary: string;
  genres: string[];
  themes: string[];
  target_audience: string[];
}

export interface PitchReadyCopy {
  key_pitch_points: string[];
  one_liner: string;
}

export interface Metadata {
  market_search_performed: boolean;
  comparable_movies_found?: number;
  analysis_timestamp?: string;
  reason?: string;
}

export interface SimilarMovies {
  Title: string;
  Year: string;
  Poster: string;
}

export interface AnalysisResponse {
  title: string;
  logline: string;
  top_level_score: TopLevelScore;
  emotional_arc_data: EmotionalArcPoint[];
  key_insights: KeyInsights;
  characters: Character[];
  pitch_ready_copy: PitchReadyCopy;
  metadata?: Metadata;
  similar_movies?: SimilarMovies[];
}
