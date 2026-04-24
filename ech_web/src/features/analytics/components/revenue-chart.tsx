"use client";

import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { DashboardSummary } from "@/features/analytics/types/dashboard";
import { toNumber } from "@/features/analytics/utils/analytics-formatters";

type RevenueChartProps = {
  data: DashboardSummary;
};

export function RevenueChart({ data }: RevenueChartProps) {
  const chartData = [
    { name: "Gross", value: toNumber(data.revenue.total_revenue) },
    { name: "Refunds", value: toNumber(data.revenue.total_refunds) },
    { name: "Net", value: toNumber(data.revenue.net_revenue) },
  ];

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
      <h2 className="text-xl font-semibold text-white">Revenue</h2>

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