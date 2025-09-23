"use client";

import { useState } from "react";
import EmotionalArcChart from "../components/EmotionalArcChart";
import { AnalysisResponse } from "../types/analysis";
import CharacterCard from "../components/CharacterCard";
import InsightsCard from "../components/InsightsCard";

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

      if (!res.ok) {
        throw new Error("Failed to analyze synopsis");
      }

      const data = await res.json();
      setAnalysis(data); // data is already story_impact_report
    } catch (err: unknown) {
      setError(err.message || "Unexpected error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-200 p-6">
      <h1 className="text-5xl font-bold my-5 text-center text-black">Film Intelligence Platform</h1>
      <h2 className="text-2xl font-bold my-3 text-black text-center">🎬 Film Story/Treatment Analyzer</h2>

      <div className="flex flex-col items-center">
  <textarea
    className="w-6xl p-3 py-5 border rounded-lg mb-3 border-gray-400 text-gray-800"
    rows={20}
    placeholder="Paste your story synopsis here..."
    value={synopsis}
    onChange={(e) => setSynopsis(e.target.value)}
  />
  <button
    onClick={handleAnalyze}
    disabled={!synopsis || loading}
    className="bg-blue-600 text-white px-4 py-2 rounded-lg shadow disabled:opacity-50"
  >
    {loading ? "Analyzing..." : "Analyze Story"}
  </button>
</div>

      {/* Error Message */}
      {error && (
        <div className="mt-4 text-red-600 bg-red-100 p-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Results */}
      {analysis && (
        <div className="mt-6 space-y-6">
          {/* Emotional Arc */}
          <div className="bg-white shadow rounded-xl p-4">
            <h2 className="text-xl font-semibold mb-2">Emotional Arc</h2>
            <EmotionalArcChart data={analysis.emotional_arc_data} />
          </div>

          {/* Characters */}
          <div className="bg-white shadow rounded-xl p-4">
            <h2 className="text-xl font-semibold mb-2">Characters</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {analysis.characters.map((c, i) => (
                <CharacterCard key={i} character={c} />
              ))}
            </div>
          </div>

          {/* Insights */}
          <InsightsCard analysis={analysis} />
        </div>
      )}
    </main>
  );
}
