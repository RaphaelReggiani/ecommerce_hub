import { apiClient } from "@/lib/api/client";
import { buildQueryString } from "@/lib/utils/build-query-string";
import type { AdminRecentActivity } from "@/features/admin-dashboard/types/admin-dashboard";

export async function getAdminDashboardRecentActivity(
  limit?: number,
): Promise<AdminRecentActivity> {
  const queryString = buildQueryString({ limit });

  return apiClient.get<AdminRecentActivity>(
    `/admin-dashboard/dashboard/activity/${queryString}`,
    { auth: true },
  );
}