import { apiClient } from "@/lib/api/client";
import { buildQueryString } from "@/lib/utils/build-query-string";
import type {
  AnalyticsPeriodFilters,
  SalesOverview,
} from "@/features/analytics/types/analytics";

export async function getSalesOverview(
  filters: AnalyticsPeriodFilters,
): Promise<SalesOverview> {
  const queryString = buildQueryString(filters);

  return apiClient.get<SalesOverview>(
    `/analytics/sales/${queryString}`,
    { auth: true },
  );
}