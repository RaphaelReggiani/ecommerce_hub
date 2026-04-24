"use client";

import { useState } from "react";

import type {
  AnalyticsPeriodFilters,
  AnalyticsPeriodType,
} from "@/features/analytics/types/analytics";

type AnalyticsFiltersProps = {
  initialFilters: AnalyticsPeriodFilters;
  onApply: (filters: AnalyticsPeriodFilters) => void;
};

export function AnalyticsFilters({
  initialFilters,
  onApply,
}: AnalyticsFiltersProps) {
  const [periodType, setPeriodType] = useState<AnalyticsPeriodType>(
    initialFilters.period_type,
  );
  const [periodStart, setPeriodStart] = useState(
    initialFilters.period_start ?? "",
  );
  const [periodEnd, setPeriodEnd] = useState(initialFilters.period_end ?? "");

  function handleApply() {
    onApply({
      period_type: periodType,
      period_start: periodStart || undefined,
      period_end: periodEnd || undefined,
    });
  }

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-5 shadow-xl">
      <div className="grid gap-4 md:grid-cols-[1fr_1fr_1fr_auto]">
        <select
          value={periodType}
          onChange={(event) =>
            setPeriodType(event.target.value as AnalyticsPeriodType)
          }
          className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-500"
        >
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
        </select>

        <input
          type="datetime-local"
          value={periodStart}
          onChange={(event) => setPeriodStart(event.target.value)}
          className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-500"
        />

        <input
          type="datetime-local"
          value={periodEnd}
          onChange={(event) => setPeriodEnd(event.target.value)}
          className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-500"
        />

        <button
          type="button"
          onClick={handleApply}
          className="rounded-2xl bg-blue-600 px-5 py-3 text-sm font-medium text-white transition hover:bg-blue-500"
        >
          Apply
        </button>
      </div>
    </div>
  );
}