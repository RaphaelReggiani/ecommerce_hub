import { useQuery } from "@tanstack/react-query";
import { getOrderFunnel } from "@/features/analytics/api/order-funnel";
import { analyticsQueryKeys } from "@/features/analytics/utils/analytics-query-keys";
import type { AnalyticsPeriodFilters } from "@/features/analytics/types/analytics";

export function useOrderFunnel(filters: AnalyticsPeriodFilters) {
  return useQuery({
    queryKey: analyticsQueryKeys.orderFunnel(filters),
    queryFn: () => getOrderFunnel(filters),
  });
}