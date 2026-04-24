"use client";

import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { ShippingOverview } from "@/features/analytics/types/analytics";

type ShippingChartProps = {
  data: ShippingOverview;
};

export function ShippingChart({ data }: ShippingChartProps) {
  const chartData = [
    { name: "In transit", value: data.shipments_in_transit },
    { name: "Delivered", value: data.shipments_delivered },
    { name: "Failed", value: data.shipments_failed },
  ];

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
      <h2 className="text-xl font-semibold text-white">Shipping</h2>

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