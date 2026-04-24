import { apiClient } from "@/lib/api/client";
import type { AdminDashboardSummary } from "@/features/admin-dashboard/types/admin-dashboard";

export async function getAdminDashboardSummary(): Promise<AdminDashboardSummary> {
  return apiClient.get<AdminDashboardSummary>(
    "/admin-dashboard/dashboard/summary/",
    { auth: true },
  );
}