import { apiClient } from "@/lib/api/client";
import { buildQueryString } from "@/lib/utils/build-query-string";
import type {
  AnalyticsPeriodFilters,
  PaymentOverview,
} from "@/features/analytics/types/analytics";

export async function getPaymentOverview(
  filters: AnalyticsPeriodFilters,
): Promise<PaymentOverview> {
  const queryString = buildQueryString(filters);

  return apiClient.get<PaymentOverview>(
    `/analytics/payments/${queryString}`,
    { auth: true },
  );
}