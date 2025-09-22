"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { EmotionalArcPoint } from "../types/analysis";

interface Props {
  data: EmotionalArcPoint[];
}

export default function EmotionalArcChart({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="point" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="intensity" stroke="#2563eb" />
      </LineChart>
    </ResponsiveContainer>
  );
}
