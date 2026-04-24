import { useQuery } from "@tanstack/react-query";
import { getDashboardSummary } from "@/features/analytics/api/dashboard-summary";
import { analyticsQueryKeys } from "@/features/analytics/utils/analytics-query-keys";
import type { AnalyticsPeriodFilters } from "@/features/analytics/types/analytics";

export function useDashboardSummary(filters: AnalyticsPeriodFilters) {
  return useQuery({
    queryKey: analyticsQueryKeys.dashboard(filters),
    queryFn: () => getDashboardSummary(filters),
  });
}