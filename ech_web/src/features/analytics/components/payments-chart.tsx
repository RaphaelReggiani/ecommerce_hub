"use client";

import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { PaymentOverview } from "@/features/analytics/types/analytics";

type PaymentsChartProps = {
  data: PaymentOverview;
};

export function PaymentsChart({ data }: PaymentsChartProps) {
  const chartData = [
    { name: "Captured", value: data.payments_captured },
    { name: "Failed", value: data.payments_failed },
    { name: "Refunded", value: data.payments_refunded },
  ];

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
      <h2 className="text-xl font-semibold text-white">Payments</h2>

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