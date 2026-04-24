import { useQuery } from "@tanstack/react-query";
import { getUserOverview } from "@/features/analytics/api/user-overview";
import { analyticsQueryKeys } from "@/features/analytics/utils/analytics-query-keys";
import type { AnalyticsPeriodFilters } from "@/features/analytics/types/analytics";

export function useUserOverview(filters: AnalyticsPeriodFilters) {
  return useQuery({
    queryKey: analyticsQueryKeys.users(filters),
    queryFn: () => getUserOverview(filters),
  });
}