export type AdminDashboardOrdersSummary = {
  total_orders: number;
  pending_orders: number;
  processing_orders: number;
  shipped_orders: number;
  delivered_orders: number;
  cancelled_orders: number;
};

export type AdminDashboardPaymentsSummary = {
  total_payments: number;
  captured_payments: number;
  failed_payments: number;
  refunded_payments: number;
  partially_refunded_payments: number;
};

export type AdminDashboardShippingSummary = {
  total_shipments: number;
  pending_shipments: number;
  in_transit_shipments: number;
  delivered_shipments: number;
  failed_shipments: number;
  returned_shipments: number;
};

export type AdminDashboardUsersSummary = {
  total_users: number;
  active_users: number;
  inactive_users: number;
  staff_users: number;
  customer_users: number;
  confirmed_users: number;
  unconfirmed_users: number;
};

export type AdminDashboardReviewsSummary = {
  total_reviews: number;
  pending_reviews: number;
  approved_reviews: number;
  rejected_reviews: number;
  hidden_reviews: number;
  cancelled_reviews: number;
};

export type AdminDashboardProductsSummary = {
  total_products: number;
  active_products: number;
  inactive_products: number;
};

export type AdminDashboardSummary = {
  orders: AdminDashboardOrdersSummary;
  payments: AdminDashboardPaymentsSummary;
  shipping: AdminDashboardShippingSummary;
  users: AdminDashboardUsersSummary;
  reviews: AdminDashboardReviewsSummary;
  products: AdminDashboardProductsSummary;
};

export type AdminDashboardOperationalMetrics = {
  orders: {
    pending_orders: number;
    processing_orders: number;
    cancelled_orders: number;
  };
  payments: {
    failed_payments: number;
    processing_payments: number;
    refunded_payments: number;
  };
  shipping: {
    delayed_shipments: number;
    failed_shipments: number;
    in_transit_shipments: number;
  };
  reviews: {
    pending_moderation: number;
    flagged_reviews: number;
    hidden_reviews: number;
  };
  notifications: {
    failed_notifications: number;
    pending_notifications: number;
    unread_notifications: number;
  };
  products: {
    low_stock_products: number;
    out_of_stock_products: number;
    products_without_images: number;
  };
};

export type AdminDashboardAlert = {
  type: string;
  severity: "critical" | "warning" | "info" | string;
  message: string;
  value: number;
};

export type AdminDashboardAlerts = {
  alerts: AdminDashboardAlert[];
  total_alerts: number;
  critical_alerts: number;
  warning_alerts: number;
  info_alerts: number;
};

export type AdminRecentActivityItem = {
  source: string;
  type: string;
  entity_id: string;
  status?: string | null;
  action_type?: string | null;
  target_module?: string | null;
  created_at: string | null;
};

export type AdminRecentActivity = {
  activities: AdminRecentActivityItem[];
  total: number;
  limit: number;
};

export type AdminDashboardEvent = {
  id: string;
  event_type: string;
  performed_by: number | null;
  performed_by_name: string | null;
  performed_by_email: string | null;
  related_log: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
};

export type AdminDashboardLifecycle = {
  started_at: string | null;
  completed_at: string | null;
  failed_at: string | null;
  created_at: string;
  updated_at: string;
};

export type AdminDashboardLogListItem = {
  id: string;
  action_type: string;
  performed_by: number | null;
  performed_by_name: string | null;
  performed_by_email: string | null;
  target_object_id: string | null;
  target_module: string | null;
  created_at: string;
};

export type AdminDashboardLogDetail = AdminDashboardLogListItem & {
  metadata: Record<string, unknown> | null;
  lifecycle: AdminDashboardLifecycle | null;
  events: AdminDashboardEvent[];
};

export type BulkOrderActionInput = {
  action_type: string;
  order_ids: string[];
};

export type BulkOrderActionResponse = {
  action: string;
  processed_orders: string[];
  total_processed: number;
};

export type BulkReviewModerationInput = {
  moderation_action: string;
  review_ids: string[];
  reason?: string;
};

export type BulkReviewModerationResponse = {
  moderation_action: string;
  processed_reviews: string[];
  total_processed: number;
};

export type BulkNotificationRetryInput = {
  notification_ids: string[];
};

export type BulkNotificationRetryResponse = {
  retried_notifications: string[];
  total_retried: number;
};

export type AdminDashboardLogFilters = {
  action_type?: string;
  performed_by?: number;
  target_module?: string;
  metadata?: string;
  created_after?: string;
  created_before?: string;
  page?: number;
};

export type AdminDashboardEventFilters = {
  event_type?: string;
  performed_by?: number;
  created_after?: string;
  created_before?: string;
  page?: number;
};