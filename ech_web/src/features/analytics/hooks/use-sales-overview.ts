import { useQuery } from "@tanstack/react-query";
import { getSalesOverview } from "@/features/analytics/api/sales-overview";
import { analyticsQueryKeys } from "@/features/analytics/utils/analytics-query-keys";
import type { AnalyticsPeriodFilters } from "@/features/analytics/types/analytics";

export function useSalesOverview(filters: AnalyticsPeriodFilters) {
  return useQuery({
    queryKey: analyticsQueryKeys.sales(filters),
    queryFn: () => getSalesOverview(filters),
  });
}