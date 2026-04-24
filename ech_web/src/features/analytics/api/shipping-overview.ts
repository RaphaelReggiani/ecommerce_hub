import { apiClient } from "@/lib/api/client";
import { buildQueryString } from "@/lib/utils/build-query-string";
import type {
  AnalyticsPeriodFilters,
  ShippingOverview,
} from "@/features/analytics/types/analytics";

export async function getShippingOverview(
  filters: AnalyticsPeriodFilters,
): Promise<ShippingOverview> {
  const queryString = buildQueryString(filters);

  return apiClient.get<ShippingOverview>(
    `/analytics/shipping/${queryString}`,
    { auth: true },
  );
}