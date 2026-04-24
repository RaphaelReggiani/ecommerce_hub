import { useQuery } from "@tanstack/react-query";
import { getProductPerformance } from "@/features/analytics/api/product-performance";
import { analyticsQueryKeys } from "@/features/analytics/utils/analytics-query-keys";
import type { AnalyticsPeriodFilters } from "@/features/analytics/types/analytics";

export function useProductPerformance(filters: AnalyticsPeriodFilters) {
  return useQuery({
    queryKey: analyticsQueryKeys.products(filters),
    queryFn: () => getProductPerformance(filters),
  });
}