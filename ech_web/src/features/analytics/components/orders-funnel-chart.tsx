"use client";

import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { OrderFunnel } from "@/features/analytics/types/analytics";

type OrdersFunnelChartProps = {
  data: OrderFunnel;
};

export function OrdersFunnelChart({ data }: OrdersFunnelChartProps) {
  const chartData = [
    { name: "Pending", value: data.pending_orders },
    { name: "Processing", value: data.processing_orders },
    { name: "Shipped", value: data.shipped_orders },
    { name: "Delivered", value: data.delivered_orders },
    { name: "Cancelled", value: data.cancelled_orders },
  ];

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
      <h2 className="text-xl font-semibold text-white">Order Funnel</h2>

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