import { apiClient } from "@/lib/api/client";
import { buildQueryString } from "@/lib/utils/build-query-string";
import type {
  AnalyticsPeriodFilters,
  ReviewOverview,
} from "@/features/analytics/types/analytics";

export async function getReviewOverview(
  filters: AnalyticsPeriodFilters,
): Promise<ReviewOverview> {
  const queryString = buildQueryString(filters);

  return apiClient.get<ReviewOverview>(
    `/analytics/reviews/${queryString}`,
    { auth: true },
  );
}