import { useQuery } from "@tanstack/react-query";
import { getCustomerSummary } from "@/features/analytics/api/customer-summary";
import { analyticsQueryKeys } from "@/features/analytics/utils/analytics-query-keys";
import type { AnalyticsPeriodFilters } from "@/features/analytics/types/analytics";

export function useCustomerSummary(filters: AnalyticsPeriodFilters) {
  return useQuery({
    queryKey: analyticsQueryKeys.customers(filters),
    queryFn: () => getCustomerSummary(filters),
  });
}