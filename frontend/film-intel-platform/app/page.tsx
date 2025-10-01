"use client";

import { useState } from "react";
import EmotionalArcChart from "../components/EmotionalArcChart";
import { AnalysisResponse } from "../types/analysis";
import CharacterCard from "../components/CharacterCard";
import InsightsCard from "../components/InsightsCard";
import PitchPointsCard from "@/components/PitchPointCard";
import SimilarMoviesCarousel from "@/components/SimilarMoviesCarousel";
import Navbar from '@/components/Navbar';

export default function Home() {
  const [synopsis, setSynopsis] = useState<string>("");
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    try {
      setLoading(true);
      setError(null);

      const res = await fetch("http://localhost:8000/analyze_synopsis", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ story: synopsis }),
      });

      if (!res.ok) throw new Error("Failed to analyze synopsis");

      const data: AnalysisResponse = await res.json();
      setAnalysis(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-950 via-gray-900 to-gray-800 text-gray-100 p-6 flex flex-col">
      <header className="text-center mb-8">
        <h2 className="text-xl font-medium text-gray-300 mt-2">
          🎬 Story & Treatment Analyzer
        </h2>
      </header>

      {/* Input Section */}
      <section className="flex flex-col items-center mb-8">
  <div className="w-full max-w-4xl">
    <textarea
      className="w-full p-4 bg-gray-800/70 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
      rows={10}
      placeholder="Paste your story synopsis here..."
      value={synopsis}
      onChange={(e) => setSynopsis(e.target.value)}
    />
    <div className="flex flex-col items-center">
    <button
      onClick={handleAnalyze}
      disabled={!synopsis || loading}
      className="mt-4 w-full max-w-2xl bg-indigo-600 text-white py-3 rounded-lg font-semibold shadow-md hover:bg-indigo-500 active:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {loading ? "Analyzing..." : "Analyze Story"}
    </button>
    </div>
  </div>
</section>

      {/* Error Message */}
      {error && (
        <div className="max-w-5xl mx-auto bg-indigo-800/80 border border-indigo-600 text-white p-4 rounded-lg mb-8 shadow-md">
          {error}
        </div>
      )}

      {/* Results Section */}
{analysis && (
  <section className="max-w-4xl mx-auto space-y-8">
    {/* Story Details (only once) */}
    <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-6 shadow-xl hover:shadow-indigo-900/20 transition">
      <h2 className="text-2xl font-semibold text-indigo-400 mb-4">Story Details</h2>
      <div className="grid grid-cols-1 gap-4 text-gray-200">
        <p><strong className="text-gray-300">Title:</strong> {analysis.title}</p>
        <p><strong className="text-gray-300">Logline:</strong> {analysis.logline}</p>
      </div>
    </div>

    {/* Insights Card (scores, genres, themes, pitch, metadata) */}
    <InsightsCard analysis={analysis} />
    {/* Key Pitch Points */}
    <PitchPointsCard pitchPoints={analysis.pitch_ready_copy.key_pitch_points} />

    {/* Emotional Arc */}
    <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-6 shadow-xl hover:shadow-indigo-900/20 transition">
      <h2 className="text-2xl font-semibold text-indigo-400 mb-4">Emotional Arc</h2>
      <EmotionalArcChart data={analysis.emotional_arc_data} />
    </div>
    
    {/* Characters */}
    <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-6 shadow-xl hover:shadow-indigo-900/20 transition">
      <h2 className="text-2xl font-semibold text-indigo-400 mb-4">Characters</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {analysis.characters.map((c, i) => (
          <CharacterCard key={i} character={c} />
        ))}
      </div>
    </div>
    
     {/* Conditionally render Similar Movies Carousel if data exists */}
    {analysis.similar_movies && analysis.similar_movies.length > 0 && (
      <SimilarMoviesCarousel similarMovies={analysis.similar_movies || []} />
    )}

  </section>
)}

    </main>
  );
}
