"use client";

import { useQuery } from "@tanstack/react-query";

import { listAdminDashboardLogs } from "@/features/admin-dashboard/api/list-logs";
import type { AdminDashboardLogFilters } from "@/features/admin-dashboard/types/admin-dashboard";
import { adminDashboardQueryKeys } from "@/features/admin-dashboard/utils/admin-dashboard-query-keys";

export function useAdminLogs(filters: AdminDashboardLogFilters = {}) {
  return useQuery({
    queryKey: adminDashboardQueryKeys.logs(filters),
    queryFn: () => listAdminDashboardLogs(filters),
  });
}