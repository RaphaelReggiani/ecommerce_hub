import { apiClient } from "@/lib/api/client";
import { buildQueryString } from "@/lib/utils/build-query-string";
import type { PaginatedApiResponse } from "@/types/api";
import type {
  AdminDashboardLogFilters,
  AdminDashboardLogListItem,
} from "@/features/admin-dashboard/types/admin-dashboard";

export async function listAdminDashboardLogs(
  filters: AdminDashboardLogFilters = {},
): Promise<PaginatedApiResponse<AdminDashboardLogListItem>> {
  const queryString = buildQueryString(filters);

  return apiClient.get<PaginatedApiResponse<AdminDashboardLogListItem>>(
    `/admin-dashboard/logs/${queryString}`,
    { auth: true },
  );
}