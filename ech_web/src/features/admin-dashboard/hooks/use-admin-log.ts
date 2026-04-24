"use client";

import { useQuery } from "@tanstack/react-query";

import { retrieveAdminDashboardLog } from "@/features/admin-dashboard/api/retrieve-log";
import { adminDashboardQueryKeys } from "@/features/admin-dashboard/utils/admin-dashboard-query-keys";

export function useAdminLog(id: string) {
  return useQuery({
    queryKey: adminDashboardQueryKeys.logDetail(id),
    queryFn: () => retrieveAdminDashboardLog(id),
    enabled: Boolean(id),
  });
}