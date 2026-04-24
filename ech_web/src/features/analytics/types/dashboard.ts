import type { AnalyticsBasePayload } from "@/features/analytics/types/analytics";

export type DashboardOrdersSummary = {
  total_orders: number;
  orders_pending: number;
  orders_processing: number;
  orders_shipped: number;
  orders_delivered: number;
  orders_cancelled: number;
};

export type DashboardRevenueSummary = {
  total_revenue: string;
  total_refunds: string;
  net_revenue: string;
};

export type DashboardPaymentsSummary = {
  payments_captured: number;
  payments_failed: number;
  payments_refunded: number;
};

export type DashboardShippingSummary = {
  shipments_in_transit: number;
  shipments_delivered: number;
  shipments_failed: number;
};

export type DashboardProductsSummary = {
  products_sold: number;
  top_product_id: string | null;
};

export type DashboardCustomersSummary = {
  active_customers: number;
  new_customers: number;
};

export type DashboardUsersSummary = {
  total_registered_users: number;
  active_users: number;
  inactive_users: number;
  confirmed_users: number;
  unconfirmed_users: number;
  staff_users: number;
  customer_users: number;
};

export type DashboardReviewsSummary = {
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

export type DashboardSummary = AnalyticsBasePayload & {
  orders: DashboardOrdersSummary;
  revenue: DashboardRevenueSummary;
  payments: DashboardPaymentsSummary;
  shipping: DashboardShippingSummary;
  products: DashboardProductsSummary;
  customers: DashboardCustomersSummary;
  users: DashboardUsersSummary;
  reviews: DashboardReviewsSummary;
};