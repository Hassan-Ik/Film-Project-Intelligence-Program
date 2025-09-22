"use client";

import { useState } from "react";
import EmotionalArcChart from "../components/EmotionalArcChart";
import { AnalysisResponse } from "../types/analysis";

export default function Home() {
  const [synopsis, setSynopsis] = useState<string>("");
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const handleAnalyze = async () => {
    setLoading(true);
    const res = await fetch("http://localhost:8000/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ synopsis }),
    });
    const data: AnalysisResponse = await res.json();
    setAnalysis(data);
    setLoading(false);
  };

  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-3xl font-bold mb-4">🎬 Story Analyzer</h1>

      <textarea
        className="w-full p-3 border rounded-lg mb-3"
        rows={5}
        placeholder="Paste your story synopsis here..."
        value={synopsis}
        onChange={(e) => setSynopsis(e.target.value)}
      />
      <button
        onClick={handleAnalyze}
        disabled={!synopsis || loading}
        className="bg-blue-600 text-white px-4 py-2 rounded-lg shadow"
      >
        {loading ? "Analyzing..." : "Analyze Story"}
      </button>

      {analysis && (
        <div className="mt-6 space-y-6">
          <div className="bg-white shadow rounded-xl p-4">
            <h2 className="text-xl font-semibold mb-2">Emotional Arc</h2>
            <EmotionalArcChart data={analysis.emotional_arc} />
          </div>

          <div className="bg-white shadow rounded-xl p-4">
            <h2 className="text-xl font-semibold mb-2">Inferred Characters</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {analysis.characters.map((c, i) => (
                <div key={i} className="border p-3 rounded-lg">
                  <p>
                    <strong>{c.name}</strong> ({c.role})
                  </p>
                  <p className="text-sm text-gray-600">{c.archetype}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white shadow rounded-xl p-4">
            <h2 className="text-xl font-semibold mb-2">Story Insights</h2>
            <p>
              <strong>Impact Score:</strong> {analysis.story_score}/100
            </p>
            <p>
              <strong>Target Audience:</strong> {analysis.audience.join(", ")}
            </p>
            <div className="flex flex-wrap gap-2 mt-2">
              {analysis.tags.map((tag, i) => (
                <span
                  key={i}
                  className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
