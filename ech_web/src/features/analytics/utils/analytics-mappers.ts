import type { AnalyticsPeriodType } from "@/features/analytics/types/analytics";

export function getAnalyticsPeriodLabel(periodType: AnalyticsPeriodType): string {
  const labels: Record<AnalyticsPeriodType, string> = {
    daily: "Daily",
    weekly: "Weekly",
    monthly: "Monthly",
  };

  return labels[periodType];
}

export function getDefaultAnalyticsFilters() {
  return {
    period_type: "daily" as AnalyticsPeriodType,
  };
}