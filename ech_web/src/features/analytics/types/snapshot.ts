import type { AnalyticsPeriodType } from "@/features/analytics/types/analytics";

export type AnalyticsEvent = {
  id: string;
  event_type: string;
  performed_by: number | null;
  performed_by_name: string | null;
  performed_by_email: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
};

export type AnalyticsSnapshotLifecycle = {
  generation_started_at: string | null;
  generation_completed_at: string | null;
  refreshed_at: string | null;
  failed_at: string | null;
  created_at: string;
  updated_at: string;
};

export type AnalyticsSnapshotListItem = {
  id: string;
  period_type: AnalyticsPeriodType;
  period_start: string;
  period_end: string;
  total_orders: number;
  total_revenue: string;
  total_refunds: string;
  net_revenue: string;
  products_sold: number;
  active_customers: number;
  total_registered_users: number;
  total_reviews: number;
  average_rating: string;
  generated_by: number | null;
  generated_by_name: string | null;
  generated_by_email: string | null;
  created_at: string;
  updated_at: string;
};

export type AnalyticsSnapshotDetail = AnalyticsSnapshotListItem & {
  orders_pending: number;
  orders_processing: number;
  orders_shipped: number;
  orders_delivered: number;
  orders_cancelled: number;
  payments_captured: number;
  payments_failed: number;
  payments_refunded: number;
  shipments_in_transit: number;
  shipments_delivered: number;
  shipments_failed: number;
  top_product_id: string | null;
  new_customers: number;
  active_users: number;
  inactive_users: number;
  confirmed_users: number;
  unconfirmed_users: number;
  staff_users: number;
  customer_users: number;
  approved_reviews: number;
  rejected_reviews: number;
  hidden_reviews: number;
  cancelled_reviews: number;
  verified_purchase_reviews: number;
  low_rated_products_count: number;
  high_rated_products_count: number;
  metadata: Record<string, unknown> | null;
  lifecycle: AnalyticsSnapshotLifecycle | null;
  events: AnalyticsEvent[];
};