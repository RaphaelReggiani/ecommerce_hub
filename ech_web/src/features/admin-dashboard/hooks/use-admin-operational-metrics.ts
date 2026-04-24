"use client";

import { useQuery } from "@tanstack/react-query";

import { getAdminDashboardOperationalMetrics } from "@/features/admin-dashboard/api/operational-metrics";
import { adminDashboardQueryKeys } from "@/features/admin-dashboard/utils/admin-dashboard-query-keys";

export function useAdminOperationalMetrics() {
  return useQuery({
    queryKey: adminDashboardQueryKeys.operationalMetrics(),
    queryFn: getAdminDashboardOperationalMetrics,
  });
}