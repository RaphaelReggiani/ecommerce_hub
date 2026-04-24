"use client";

import { useQuery } from "@tanstack/react-query";

import { getAdminDashboardAlerts } from "@/features/admin-dashboard/api/alerts";
import { adminDashboardQueryKeys } from "@/features/admin-dashboard/utils/admin-dashboard-query-keys";

export function useAdminAlerts() {
  return useQuery({
    queryKey: adminDashboardQueryKeys.alerts(),
    queryFn: getAdminDashboardAlerts,
  });
}