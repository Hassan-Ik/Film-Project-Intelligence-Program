"use client";

export default function PitchPointsCard({ pitchPoints }: { pitchPoints: string[] }) {
  return (
    <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-6 shadow-xl hover:shadow-indigo-900/20 transition max-w-4xl mx-auto">
      <h2 className="text-2xl font-semibold text-indigo-400 mb-4">Key Pitch Points</h2>
      <ul className="list-disc list-inside space-y-2 text-gray-300 text-lg">
        {pitchPoints.map((point, i) => (
          <li key={i}>{point}</li>
        ))}
      </ul>
    </div>
  );
}
