import { apiClient } from "@/lib/api/client";
import type { AdminDashboardLogDetail } from "@/features/admin-dashboard/types/admin-dashboard";

export async function retrieveAdminDashboardLog(
  id: string,
): Promise<AdminDashboardLogDetail> {
  return apiClient.get<AdminDashboardLogDetail>(
    `/admin-dashboard/logs/${id}/`,
    { auth: true },
  );
}