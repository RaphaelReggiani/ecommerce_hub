import { useQuery } from "@tanstack/react-query";
import { getPaymentOverview } from "@/features/analytics/api/payment-overview";
import { analyticsQueryKeys } from "@/features/analytics/utils/analytics-query-keys";
import type { AnalyticsPeriodFilters } from "@/features/analytics/types/analytics";

export function usePaymentOverview(filters: AnalyticsPeriodFilters) {
  return useQuery({
    queryKey: analyticsQueryKeys.payments(filters),
    queryFn: () => getPaymentOverview(filters),
  });
}