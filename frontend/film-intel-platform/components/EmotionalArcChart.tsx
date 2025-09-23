"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { EmotionalArcPoint } from "../types/analysis";

interface Props {
  data: EmotionalArcPoint[];
}

export default function EmotionalArcChart({ data }: Props) {
  return (
    <div className="w-full h-64">
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 20, right: 20, left: 0, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="point"
            tick={{ fontSize: 12 }}
            interval={0}
          />
          <YAxis
            label={{ value: "Intensity", angle: -90, position: "insideLeft" }}
            tick={{ fontSize: 12 }}
          />
          <Tooltip
            formatter={(value, name, props) => [`${value}`, "Intensity"]}
            labelFormatter={(label) => `Point: ${label}`}
          />
          <ReferenceLine y={0} stroke="#9ca3af" strokeDasharray="3 3" /> {/* Baseline */}
          <Line
            type="monotone"
            dataKey="intensity"
            stroke="#2563eb"
            strokeWidth={2}
            dot={{ r: 4, fill: "#2563eb" }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
