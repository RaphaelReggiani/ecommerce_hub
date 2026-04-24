"use client";

import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { UserOverview } from "@/features/analytics/types/analytics";

type UsersChartProps = {
  data: UserOverview;
};

export function UsersChart({ data }: UsersChartProps) {
  const chartData = [
    { name: "Active", value: data.active_users },
    { name: "Inactive", value: data.inactive_users },
    { name: "Confirmed", value: data.confirmed_users },
    { name: "Unconfirmed", value: data.unconfirmed_users },
    { name: "Staff", value: data.staff_users },
    { name: "Customers", value: data.customer_users },
  ];

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
      <h2 className="text-xl font-semibold text-white">Users</h2>

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