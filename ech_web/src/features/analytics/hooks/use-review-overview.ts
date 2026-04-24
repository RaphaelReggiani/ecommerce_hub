import { useQuery } from "@tanstack/react-query";
import { getReviewOverview } from "@/features/analytics/api/review-overview";
import { analyticsQueryKeys } from "@/features/analytics/utils/analytics-query-keys";
import type { AnalyticsPeriodFilters } from "@/features/analytics/types/analytics";

export function useReviewOverview(filters: AnalyticsPeriodFilters) {
  return useQuery({
    queryKey: analyticsQueryKeys.reviews(filters),
    queryFn: () => getReviewOverview(filters),
  });
}