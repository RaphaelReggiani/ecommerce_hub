"use client";

import { useQuery } from "@tanstack/react-query";

import { listAdminDashboardEvents } from "@/features/admin-dashboard/api/list-events";
import type { AdminDashboardEventFilters } from "@/features/admin-dashboard/types/admin-dashboard";
import { adminDashboardQueryKeys } from "@/features/admin-dashboard/utils/admin-dashboard-query-keys";

export function useAdminEvents(filters: AdminDashboardEventFilters = {}) {
  return useQuery({
    queryKey: adminDashboardQueryKeys.events(filters),
    queryFn: () => listAdminDashboardEvents(filters),
  });
}