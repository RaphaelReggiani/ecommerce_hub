"use client";

import { useQuery } from "@tanstack/react-query";

import { getAdminDashboardRecentActivity } from "@/features/admin-dashboard/api/recent-activity";
import { adminDashboardQueryKeys } from "@/features/admin-dashboard/utils/admin-dashboard-query-keys";

export function useAdminRecentActivity(limit = 20) {
  return useQuery({
    queryKey: adminDashboardQueryKeys.recentActivity(limit),
    queryFn: () => getAdminDashboardRecentActivity(limit),
  });
}