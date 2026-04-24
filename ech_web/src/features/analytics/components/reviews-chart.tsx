"use client";

import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { ReviewOverview } from "@/features/analytics/types/analytics";

type ReviewsChartProps = {
  data: ReviewOverview;
};

export function ReviewsChart({ data }: ReviewsChartProps) {
  const chartData = [
    { name: "Approved", value: data.approved_reviews },
    { name: "Rejected", value: data.rejected_reviews },
    { name: "Hidden", value: data.hidden_reviews },
    { name: "Cancelled", value: data.cancelled_reviews },
    { name: "Verified", value: data.verified_purchase_reviews },
  ];

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
      <h2 className="text-xl font-semibold text-white">Reviews</h2>

      <div className="mt-6 h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <XAxis dataKey="name" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip />
            <Bar dataKey="value" fill="#2563eb" radius={[10, 10, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}