import { apiClient } from "@/lib/api/client";
import { buildQueryString } from "@/lib/utils/build-query-string";
import type { PaginatedApiResponse } from "@/types/api";
import type { AnalyticsPeriodType } from "@/features/analytics/types/analytics";
import type { AnalyticsSnapshotListItem } from "@/features/analytics/types/snapshot";

export type ListSnapshotsFilters = {
  period_type?: AnalyticsPeriodType;
  generated_by?: number;
  period_start_after?: string;
  period_start_before?: string;
  period_end_after?: string;
  period_end_before?: string;
  total_revenue_min?: number;
  total_revenue_max?: number;
  total_orders_min?: number;
  total_orders_max?: number;
  average_rating_min?: number;
  average_rating_max?: number;
  page?: number;
};

export async function listSnapshots(
  filters: ListSnapshotsFilters = {},
): Promise<PaginatedApiResponse<AnalyticsSnapshotListItem>> {
  const queryString = buildQueryString(filters);

  return apiClient.get<PaginatedApiResponse<AnalyticsSnapshotListItem>>(
    `/analytics/snapshots/${queryString}`,
    { auth: true },
  );
}