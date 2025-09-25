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
    <div className="w-full h-80 bg-gray-800 p-4 rounded-xl shadow-lg">
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 20, right: 30, left: 10, bottom: 20 }}>
          <CartesianGrid stroke="#4b5563" strokeDasharray="3 3" />
          <XAxis
            dataKey="point"
            tick={{ fill: "#d1d5db", fontSize: 12 }}
            interval={0}
            stroke="#d1d5db"
          />
          <YAxis
            label={{
              value: "Emotional Intensity",
              angle: -90,
              position: "insideLeft",
              fill: "#d1d5db",
              fontSize: 14,
            }}
            tick={{ fill: "#d1d5db", fontSize: 12 }}
            stroke="#d1d5db"
          />
          <Tooltip
            formatter={(value, name, props) => [`${value}`, "Intensity"]}
            labelFormatter={(label) => `Story Point: ${label}`}
            contentStyle={{
              backgroundColor: "#1f2937",
              border: "1px solid #4b5563",
              borderRadius: "8px",
              color: "#f3f4f6",
            }}
            itemStyle={{ color: "#f3f4f6" }}
          />
          <ReferenceLine y={0} stroke="#6b7280" strokeDasharray="3 3" />
          <Line
            type="monotone"
            dataKey="intensity"
            stroke="#6366f1"
            strokeWidth={3}
            dot={{ r: 5, fill: "#6366f1", stroke: "#fff", strokeWidth: 2 }}
            activeDot={{ r: 7, fill: "#a5b4fc", stroke: "#fff", strokeWidth: 2 }}
            animationDuration={1000}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}