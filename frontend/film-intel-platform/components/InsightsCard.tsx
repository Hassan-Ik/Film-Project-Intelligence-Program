"use client";

import { useState } from "react";
import { AnalysisResponse } from "../types/analysis";
import { ChevronDown, ChevronUp } from "lucide-react";

function ScoreCard({ label, value }: { label: string; value: number }) {
  const radius = 15.9155; // matches your path
  const circumference = 2 * Math.PI * radius; // total length of the circle
  const offset = circumference - (value / 100) * circumference; // fill based on value

  return (
    <div className="flex flex-col items-center mb-6">
      <div className="relative w-24 h-24">
        <svg className="w-full h-full" viewBox="0 0 36 36">
          <path
            className="fill-none stroke-gray-700"
            d="M18 2.0845a15.9155 15.9155 0 0 1 0 31.831a15.9155 15.9155 0 0 1 0-31.831"
            strokeWidth="4"
          />
          <path
            className="fill-none stroke-indigo-500"
            d="M18 2.0845a15.9155 15.9155 0 0 1 0 31.831a15.9155 15.9155 0 0 1 0-31.831"
            strokeWidth="4"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-lg font-semibold text-gray-100">
          {value}%
        </div>
      </div>
      <p className="mt-2 text-sm font-medium text-gray-300">{label}</p>
    </div>
  );
}


function MetadataCard({ metadata }: { metadata?: AnalysisResponse["metadata"] }) {
  const [open, setOpen] = useState(false);
  if (!metadata) return null;

  return (
    <div className="mt-6">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center text-sm text-indigo-400 hover:text-indigo-300 transition-colors"
      >
        {open ? <ChevronUp className="w-4 h-4 mr-1" /> : <ChevronDown className="w-4 h-4 mr-1" />}
        {open ? "Hide Analysis Metadata" : "Show Analysis Metadata"}
      </button>

      {open && (
        <div className="mt-3 bg-gray-700 p-4 rounded-lg text-sm text-gray-200 space-y-2">
          <p>
            Market Search: {metadata.market_search_performed ? "✅ Yes" : "❌ No"}
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
    <div className="bg-gray-900/80 shadow-xl rounded-xl p-6 hover:shadow-indigo-900/20 transition">
      <h2 className="text-2xl font-semibold text-indigo-300 mb-4">📊 Story Insights</h2>

      {/* Scores */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
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
      <div className="mb-6">
        <p className="font-medium text-sm text-gray-200 mb-2">Genres</p>
        <div className="flex flex-wrap gap-2">
          {analysis.key_insights.genres.map((g, i) => (
            <span
              key={i}
              className="px-3 py-1 bg-indigo-900 text-indigo-300 text-sm rounded-full"
            >
              {g}
            </span>
          ))}
        </div>
      </div>

      <div className="mb-6">
        <p className="font-medium text-sm text-gray-200 mb-2">Themes</p>
        <div className="flex flex-wrap gap-2">
          {analysis.key_insights.themes.map((t, i) => (
            <span
              key={i}
              className="px-3 py-1 bg-green-900 text-green-300 text-sm rounded-full"
            >
              {t}
            </span>
          ))}
        </div>
      </div>

      {/* Target Audience */}
      <div className="mb-6">
        <p className="font-medium text-sm text-gray-200 mb-1">🎯 Target Audience</p>
        <p className="text-gray-300">{analysis.key_insights.target_audience.join(", ")}</p>
      </div>

      {/* Summary */}
      <div className="mb-6">
        <p className="font-medium text-sm text-gray-200 mb-1">Summary</p>
        <p className="italic text-gray-300">{analysis.key_insights.summary}</p>
      </div>

      {/* One-Liner Pitch */}
      <div className="bg-indigo-900 border-l-4 border-indigo-500 p-4 rounded-lg mb-6">
        <h3 className="font-semibold text-indigo-300">🎯 One-Liner Pitch</h3>
        <p className="italic text-gray-200 mt-1">{analysis.pitch_ready_copy.one_liner}</p>
      </div>

      {/* Metadata */}
      {/* <MetadataCard metadata={analysis.metadata} /> */}
    </div>
  );
}
