import { apiClient } from "@/lib/api/client";
import { buildQueryString } from "@/lib/utils/build-query-string";
import type { PaginatedApiResponse } from "@/types/api";
import type {
  AdminDashboardEvent,
  AdminDashboardEventFilters,
} from "@/features/admin-dashboard/types/admin-dashboard";

export async function listAdminDashboardEvents(
  filters: AdminDashboardEventFilters = {},
): Promise<PaginatedApiResponse<AdminDashboardEvent>> {
  const queryString = buildQueryString(filters);

  return apiClient.get<PaginatedApiResponse<AdminDashboardEvent>>(
    `/admin-dashboard/events/${queryString}`,
    { auth: true },
  );
}