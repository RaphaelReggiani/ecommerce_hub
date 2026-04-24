import { apiClient } from "@/lib/api/client";
import type { AdminDashboardOperationalMetrics } from "@/features/admin-dashboard/types/admin-dashboard";

export async function getAdminDashboardOperationalMetrics(): Promise<AdminDashboardOperationalMetrics> {
  return apiClient.get<AdminDashboardOperationalMetrics>(
    "/admin-dashboard/dashboard/operational-metrics/",
    { auth: true },
  );
}