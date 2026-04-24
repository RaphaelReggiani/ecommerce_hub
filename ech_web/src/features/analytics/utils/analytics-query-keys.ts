import type { AnalyticsPeriodFilters } from "@/features/analytics/types/analytics";

export const analyticsQueryKeys = {
  all: ["analytics"] as const,

  dashboard: (filters: AnalyticsPeriodFilters) =>
    ["analytics", "dashboard", filters] as const,

  sales: (filters: AnalyticsPeriodFilters) =>
    ["analytics", "sales", filters] as const,

  orderFunnel: (filters: AnalyticsPeriodFilters) =>
    ["analytics", "orders", "funnel", filters] as const,

  payments: (filters: AnalyticsPeriodFilters) =>
    ["analytics", "payments", filters] as const,

  shipping: (filters: AnalyticsPeriodFilters) =>
    ["analytics", "shipping", filters] as const,

  products: (filters: AnalyticsPeriodFilters) =>
    ["analytics", "products", "performance", filters] as const,

  customers: (filters: AnalyticsPeriodFilters) =>
    ["analytics", "customers", filters] as const,

  users: (filters: AnalyticsPeriodFilters) =>
    ["analytics", "users", filters] as const,

  reviews: (filters: AnalyticsPeriodFilters) =>
    ["analytics", "reviews", filters] as const,

  snapshots: (filters?: Record<string, unknown>) =>
    ["analytics", "snapshots", filters ?? {}] as const,

  snapshotDetail: (id: string) =>
    ["analytics", "snapshots", "detail", id] as const,
};