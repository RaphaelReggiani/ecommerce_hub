export type AnalyticsPeriodType = "daily" | "weekly" | "monthly";

export type AnalyticsPeriodFilters = {
  period_type: AnalyticsPeriodType;
  period_start?: string;
  period_end?: string;
};

export type AnalyticsBasePayload = {
  source: string;
  snapshot_id: string | null;
  period_type: AnalyticsPeriodType | null;
  period_start: string | null;
  period_end: string;
};

export type SalesOverview = AnalyticsBasePayload & {
  total_orders: number;
  delivered_orders: number;
  cancelled_orders: number;
  total_revenue: string;
  total_refunds: string;
  net_revenue: string;
  average_order_value: string;
  payments_captured: number;
  payments_refunded: number;
};

export type OrderFunnel = AnalyticsBasePayload & {
  total_orders: number;
  pending_orders: number;
  processing_orders: number;
  shipped_orders: number;
  delivered_orders: number;
  cancelled_orders: number;
  delivered_rate: number;
  cancelled_rate: number;
};

export type PaymentOverview = AnalyticsBasePayload & {
  payments_captured: number;
  payments_failed: number;
  payments_refunded: number;
};

export type ShippingOverview = AnalyticsBasePayload & {
  shipments_in_transit: number;
  shipments_delivered: number;
  shipments_failed: number;
};

export type ProductPerformance = AnalyticsBasePayload & {
  products_sold: number;
  top_product_id: string | null;
};

export type CustomerSummary = AnalyticsBasePayload & {
  active_customers: number;
  new_customers: number;
  customer_growth: number;
  repeat_customer_rate: number;
};

export type UserOverview = AnalyticsBasePayload & {
  total_registered_users: number;
  active_users: number;
  inactive_users: number;
  confirmed_users: number;
  unconfirmed_users: number;
  staff_users: number;
  customer_users: number;
};

export type ReviewOverview = AnalyticsBasePayload & {
  total_reviews: number;
  approved_reviews: number;
  rejected_reviews: number;
  hidden_reviews: number;
  cancelled_reviews: number;
  verified_purchase_reviews: number;
  average_rating: string;
  low_rated_products_count: number;
  high_rated_products_count: number;
};