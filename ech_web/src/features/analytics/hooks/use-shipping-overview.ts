import { useQuery } from "@tanstack/react-query";
import { getShippingOverview } from "@/features/analytics/api/shipping-overview";
import { analyticsQueryKeys } from "@/features/analytics/utils/analytics-query-keys";
import type { AnalyticsPeriodFilters } from "@/features/analytics/types/analytics";

export function useShippingOverview(filters: AnalyticsPeriodFilters) {
  return useQuery({
    queryKey: analyticsQueryKeys.shipping(filters),
    queryFn: () => getShippingOverview(filters),
  });
}