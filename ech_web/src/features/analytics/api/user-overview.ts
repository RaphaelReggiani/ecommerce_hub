import { apiClient } from "@/lib/api/client";
import { buildQueryString } from "@/lib/utils/build-query-string";
import type {
  AnalyticsPeriodFilters,
  UserOverview,
} from "@/features/analytics/types/analytics";

export async function getUserOverview(
  filters: AnalyticsPeriodFilters,
): Promise<UserOverview> {
  const queryString = buildQueryString(filters);

  return apiClient.get<UserOverview>(
    `/analytics/users/${queryString}`,
    { auth: true },
  );
}