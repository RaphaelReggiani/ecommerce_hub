"use client";

import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { CustomerSummary } from "@/features/analytics/types/analytics";

type CustomersChartProps = {
  data: CustomerSummary;
};

export function CustomersChart({ data }: CustomersChartProps) {
  const chartData = [
    { name: "Active", value: data.active_customers },
    { name: "New", value: data.new_customers },
    { name: "Growth", value: data.customer_growth },
    { name: "Repeat rate", value: data.repeat_customer_rate },
  ];

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
      <h2 className="text-xl font-semibold text-white">Customers</h2>

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