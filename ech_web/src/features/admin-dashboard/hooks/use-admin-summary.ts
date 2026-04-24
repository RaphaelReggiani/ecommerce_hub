"use client";

import { useQuery } from "@tanstack/react-query";

import { getAdminDashboardSummary } from "@/features/admin-dashboard/api/summary";
import { adminDashboardQueryKeys } from "@/features/admin-dashboard/utils/admin-dashboard-query-keys";

export function useAdminSummary() {
  return useQuery({
    queryKey: adminDashboardQueryKeys.summary(),
    queryFn: getAdminDashboardSummary,
  });
}