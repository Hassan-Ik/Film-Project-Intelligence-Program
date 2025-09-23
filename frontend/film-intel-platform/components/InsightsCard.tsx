"use client";

import { useState } from "react";
import { AnalysisResponse } from "../types/analysis";
import { Progress } from "@/components/ui/progress";
import { ChevronDown, ChevronUp } from "lucide-react";

function ScoreCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="mb-3">
      <p className="text-sm font-medium">{label}</p>
      <Progress value={value} className="h-2 mt-1" />
      <p className="text-xs text-gray-500 mt-1">{value}/100</p>
    </div>
  );
}

function MetadataCard({ metadata }: { metadata?: AnalysisResponse["metadata"] }) {
  const [open, setOpen] = useState(false);
  if (!metadata) return null;

  return (
    <div className="mt-4">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center text-sm text-blue-600 hover:text-blue-800"
      >
        {open ? <ChevronUp className="w-4 h-4 mr-1" /> : <ChevronDown className="w-4 h-4 mr-1" />}
        {open ? "Hide Analysis Metadata" : "Show Analysis Metadata"}
      </button>

      {open && (
        <div className="mt-2 bg-gray-100 p-3 rounded-lg text-sm text-gray-700 space-y-1">
          <p>
            Market Search:{" "}
            {metadata.market_search_performed ? "✅ Yes" : "❌ No"}
          </p>
          {metadata.comparable_movies_found !== undefined && (
            <p>Comparable Movies Found: {metadata.comparable_movies_found}</p>
          )}
          {metadata.analysis_timestamp && (
            <p>Timestamp: {metadata.analysis_timestamp}</p>
          )}
          {metadata.reason && <p>Reason: {metadata.reason}</p>}
        </div>
      )}
    </div>
  );
}

export default function InsightsCard({ analysis }: { analysis: AnalysisResponse }) {
  return (
    <div className="bg-white shadow rounded-xl p-6">
      <h2 className="text-xl font-semibold mb-4">📊 Story Insights</h2>

      {/* Title & Logline */}
      <p className="text-lg font-semibold text-gray-800">{analysis.title}</p>
      <p className="italic text-gray-600 mb-4">“{analysis.logline}”</p>

      {/* Scores */}
      <div className="mb-6">
        <ScoreCard label="Overall" value={analysis.top_level_score.overall} />
        <ScoreCard
          label="Narrative Strength"
          value={analysis.top_level_score.narrative_strength}
        />
        <ScoreCard
          label="Market Fit"
          value={analysis.top_level_score.market_fit}
        />
      </div>

      {/* Genres & Themes */}
      <div className="mb-4">
        <p className="font-medium text-sm mb-2">Genres</p>
        <div className="flex flex-wrap gap-2">
          {analysis.key_insights.genres.map((g, i) => (
            <span
              key={i}
              className="px-2 py-1 bg-purple-100 text-purple-700 text-sm rounded-full"
            >
              {g}
            </span>
          ))}
        </div>
      </div>

      <div className="mb-4">
        <p className="font-medium text-sm mb-2">Themes</p>
        <div className="flex flex-wrap gap-2">
          {analysis.key_insights.themes.map((t, i) => (
            <span
              key={i}
              className="px-2 py-1 bg-green-100 text-green-700 text-sm rounded-full"
            >
              {t}
            </span>
          ))}
        </div>
      </div>

      {/* Target Audience */}
      <div className="mb-4">
        <p className="font-medium text-sm mb-1">🎯 Target Audience</p>
        <p className="text-gray-700">
          {analysis.key_insights.target_audience.join(", ")}
        </p>
      </div>

      {/* Summary */}
      <div className="mb-4">
        <p className="font-medium text-sm mb-1">Summary</p>
        <p className="italic text-gray-700">{analysis.key_insights.summary}</p>
      </div>

      {/* One-Liner Pitch */}
      <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded-lg mt-6">
        <h3 className="font-semibold text-blue-800">🎯 One-Liner Pitch</h3>
        <p className="italic text-blue-900 mt-1">
          {analysis.pitch_ready_copy.one_liner}
        </p>
      </div>

      {/* Metadata */}
      <MetadataCard metadata={analysis.metadata} />
    </div>
  );
}
