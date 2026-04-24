import { apiClient } from "@/lib/api/client";
import type { AdminDashboardAlerts } from "@/features/admin-dashboard/types/admin-dashboard";

export async function getAdminDashboardAlerts(): Promise<AdminDashboardAlerts> {
  return apiClient.get<AdminDashboardAlerts>(
    "/admin-dashboard/dashboard/alerts/",
    { auth: true },
  );
}