"use client";

import { Character } from "../types/analysis";
import { User } from "lucide-react";

export default function CharacterCard({ character }: { character: Character }) {
  return (
    <div className="border border-gray-700 rounded-xl p-6 bg-gray-800 shadow-lg hover:shadow-xl transition-shadow duration-300">
      {/* Role + Icon */}
      <div className="flex items-center mb-4">
        <User className="w-6 h-6 text-indigo-500 mr-3" />
        <h3 className="text-lg font-semibold text-gray-100">{character.role}</h3>
      </div>

      {/* Short Description */}
      <p className="text-sm text-gray-300 mb-4 line-clamp-3">{character.description_short}</p>

      {/* Archetype */}
      <span className="inline-block px-3 py-1 text-xs font-medium bg-indigo-900 text-indigo-300 rounded-full mb-4">
        {character.attributes.archetype}
      </span>

      {/* Audience Appeal Score */}
      <div className="mb-4">
        <p className="text-sm font-medium text-gray-200 mb-1">⭐ Audience Appeal</p>
        <div className="relative w-full h-2 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="absolute top-0 left-0 h-full bg-indigo-500 transition-all duration-500"
            style={{ width: `${character.attributes.audience_appeal_score * 10}%` }}
          />
        </div>
        <p className="text-xs text-gray-400 mt-1">
          {character.attributes.audience_appeal_score}/10
        </p>
      </div>

      {/* Comparable Actors */}
      <div>
        <p className="text-sm font-medium text-gray-200 mb-2">👥 Comparable Actors</p>
        <div className="flex flex-wrap gap-2">
          {character.attributes.comparable_actors.map((actor, i) => (
            <span
              key={i}
              className="px-3 py-1 bg-gray-700 text-gray-200 rounded-full text-xs font-medium"
            >
              {actor}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}