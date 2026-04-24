import { apiClient } from "@/lib/api/client";
import { buildQueryString } from "@/lib/utils/build-query-string";
import type { AnalyticsPeriodFilters } from "@/features/analytics/types/analytics";
import type { DashboardSummary } from "@/features/analytics/types/dashboard";

export async function getDashboardSummary(
  filters: AnalyticsPeriodFilters,
): Promise<DashboardSummary> {
  const queryString = buildQueryString(filters);

  return apiClient.get<DashboardSummary>(
    `/analytics/dashboard/${queryString}`,
    { auth: true },
  );
}