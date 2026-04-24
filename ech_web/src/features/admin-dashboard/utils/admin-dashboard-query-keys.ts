import type {
  AdminDashboardEventFilters,
  AdminDashboardLogFilters,
} from "@/features/admin-dashboard/types/admin-dashboard";

export const adminDashboardQueryKeys = {
  all: ["admin-dashboard"] as const,

  summary: () => ["admin-dashboard", "summary"] as const,

  operationalMetrics: () =>
    ["admin-dashboard", "operational-metrics"] as const,

  alerts: () => ["admin-dashboard", "alerts"] as const,

  recentActivity: (limit?: number) =>
    ["admin-dashboard", "recent-activity", { limit }] as const,

  logs: (filters: AdminDashboardLogFilters = {}) =>
    ["admin-dashboard", "logs", filters] as const,

  logDetail: (id: string) =>
    ["admin-dashboard", "logs", "detail", id] as const,

  events: (filters: AdminDashboardEventFilters = {}) =>
    ["admin-dashboard", "events", filters] as const,
};