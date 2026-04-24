import { apiClient } from "@/lib/api/client";
import { buildQueryString } from "@/lib/utils/build-query-string";
import type {
  AnalyticsPeriodFilters,
  ProductPerformance,
} from "@/features/analytics/types/analytics";

export async function getProductPerformance(
  filters: AnalyticsPeriodFilters,
): Promise<ProductPerformance> {
  const queryString = buildQueryString(filters);

  return apiClient.get<ProductPerformance>(
    `/analytics/products/performance/${queryString}`,
    { auth: true },
  );
}