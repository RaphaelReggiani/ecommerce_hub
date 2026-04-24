import { apiClient } from "@/lib/api/client";
import { buildQueryString } from "@/lib/utils/build-query-string";
import type {
  AnalyticsPeriodFilters,
  OrderFunnel,
} from "@/features/analytics/types/analytics";

export async function getOrderFunnel(
  filters: AnalyticsPeriodFilters,
): Promise<OrderFunnel> {
  const queryString = buildQueryString(filters);

  return apiClient.get<OrderFunnel>(
    `/analytics/orders/funnel/${queryString}`,
    { auth: true },
  );
}