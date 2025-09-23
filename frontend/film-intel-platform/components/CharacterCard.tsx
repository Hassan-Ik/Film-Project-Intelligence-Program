"use client";

import { Character } from "../types/analysis";
import { Progress } from "@/components/ui/progress";
import { User } from "lucide-react";

export default function CharacterCard({ character }: { character: Character }) {
  return (
    <div className="border rounded-xl p-4 shadow-sm bg-white">
      {/* Role + Icon */}
      <div className="flex items-center mb-2">
        <User className="w-5 h-5 text-blue-600 mr-2" />
        <h3 className="font-semibold text-gray-800">{character.role}</h3>
      </div>

      {/* Short Description */}
      <p className="text-sm text-gray-600 mb-3">{character.description_short}</p>

      {/* Archetype */}
      <span className="inline-block px-2 py-1 text-xs font-medium bg-purple-100 text-purple-700 rounded-full mb-3">
        {character.attributes.archetype}
      </span>

      {/* Audience Appeal Score */}
      <div className="mb-3">
        <p className="text-sm font-medium">⭐ Audience Appeal</p>
        <Progress
          value={character.attributes.audience_appeal_score * 10} // convert 1–10 to %
          className="h-2 mt-1"
        />
        <p className="text-xs text-gray-500 mt-1">
          {character.attributes.audience_appeal_score}/10
        </p>
      </div>

      {/* Comparable Actors */}
      <div>
        <p className="text-sm font-medium mb-1">👥 Comparable Actors</p>
        <div className="flex flex-wrap gap-2">
          {character.attributes.comparable_actors.map((actor, i) => (
            <span
              key={i}
              className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs"
            >
              {actor}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
