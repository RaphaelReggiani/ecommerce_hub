export type StatusTone =
  | "default"
  | "info"
  | "warning"
  | "success"
  | "danger"
  | "muted";

export const ORDER_STATUS = {
  pending: "pending",
  confirmed: "confirmed",
  processing: "processing",
  shipped: "shipped",
  delivered: "delivered",
  cancelled: "cancelled",
  refunded: "refunded",
} as const;

export const PAYMENT_STATUS = {
  pending: "pending",
  processing: "processing",
  authorized: "authorized",
  captured: "captured",
  failed: "failed",
  cancelled: "cancelled",
  partially_refunded: "partially_refunded",
  refunded: "refunded",
} as const;

export const SHIPPING_STATUS = {
  pending: "pending",
  preparing: "preparing",
  shipped: "shipped",
  in_transit: "in_transit",
  delivered: "delivered",
  failed: "failed",
  returned: "returned",
  cancelled: "cancelled",
} as const;

export const REVIEW_STATUS = {
  pending: "pending",
  approved: "approved",
  rejected: "rejected",
  hidden: "hidden",
  cancelled: "cancelled",
} as const;

export const NOTIFICATION_STATUS = {
  pending: "pending",
  unread: "unread",
  read: "read",
  archived: "archived",
  cancelled: "cancelled",
  failed: "failed",
} as const;

export const SNAPSHOT_PERIOD = {
  daily: "daily",
  weekly: "weekly",
  monthly: "monthly",
} as const;

export const ADMIN_ALERT_SEVERITY = {
  critical: "critical",
  warning: "warning",
  info: "info",
} as const;

export const ORDER_STATUS_LABELS = {
  [ORDER_STATUS.pending]: "Pending",
  [ORDER_STATUS.confirmed]: "Confirmed",
  [ORDER_STATUS.processing]: "Processing",
  [ORDER_STATUS.shipped]: "Shipped",
  [ORDER_STATUS.delivered]: "Delivered",
  [ORDER_STATUS.cancelled]: "Cancelled",
  [ORDER_STATUS.refunded]: "Refunded",
} as const;

export const PAYMENT_STATUS_LABELS = {
  [PAYMENT_STATUS.pending]: "Pending",
  [PAYMENT_STATUS.processing]: "Processing",
  [PAYMENT_STATUS.authorized]: "Authorized",
  [PAYMENT_STATUS.captured]: "Captured",
  [PAYMENT_STATUS.failed]: "Failed",
  [PAYMENT_STATUS.cancelled]: "Cancelled",
  [PAYMENT_STATUS.partially_refunded]: "Partially refunded",
  [PAYMENT_STATUS.refunded]: "Refunded",
} as const;

export const SHIPPING_STATUS_LABELS = {
  [SHIPPING_STATUS.pending]: "Pending",
  [SHIPPING_STATUS.preparing]: "Preparing",
  [SHIPPING_STATUS.shipped]: "Shipped",
  [SHIPPING_STATUS.in_transit]: "In transit",
  [SHIPPING_STATUS.delivered]: "Delivered",
  [SHIPPING_STATUS.failed]: "Failed",
  [SHIPPING_STATUS.returned]: "Returned",
  [SHIPPING_STATUS.cancelled]: "Cancelled",
} as const;

export const REVIEW_STATUS_LABELS = {
  [REVIEW_STATUS.pending]: "Pending",
  [REVIEW_STATUS.approved]: "Approved",
  [REVIEW_STATUS.rejected]: "Rejected",
  [REVIEW_STATUS.hidden]: "Hidden",
  [REVIEW_STATUS.cancelled]: "Cancelled",
} as const;

export const NOTIFICATION_STATUS_LABELS = {
  [NOTIFICATION_STATUS.pending]: "Pending",
  [NOTIFICATION_STATUS.unread]: "Unread",
  [NOTIFICATION_STATUS.read]: "Read",
  [NOTIFICATION_STATUS.archived]: "Archived",
  [NOTIFICATION_STATUS.cancelled]: "Cancelled",
  [NOTIFICATION_STATUS.failed]: "Failed",
} as const;

export const SNAPSHOT_PERIOD_LABELS = {
  [SNAPSHOT_PERIOD.daily]: "Daily",
  [SNAPSHOT_PERIOD.weekly]: "Weekly",
  [SNAPSHOT_PERIOD.monthly]: "Monthly",
} as const;

export const ADMIN_ALERT_SEVERITY_LABELS = {
  [ADMIN_ALERT_SEVERITY.critical]: "Critical",
  [ADMIN_ALERT_SEVERITY.warning]: "Warning",
  [ADMIN_ALERT_SEVERITY.info]: "Info",
} as const;

export const ORDER_STATUS_TONES = {
  [ORDER_STATUS.pending]: "warning",
  [ORDER_STATUS.confirmed]: "info",
  [ORDER_STATUS.processing]: "info",
  [ORDER_STATUS.shipped]: "info",
  [ORDER_STATUS.delivered]: "success",
  [ORDER_STATUS.cancelled]: "danger",
  [ORDER_STATUS.refunded]: "muted",
} as const satisfies Record<keyof typeof ORDER_STATUS_LABELS, StatusTone>;

export const PAYMENT_STATUS_TONES = {
  [PAYMENT_STATUS.pending]: "warning",
  [PAYMENT_STATUS.processing]: "info",
  [PAYMENT_STATUS.authorized]: "info",
  [PAYMENT_STATUS.captured]: "success",
  [PAYMENT_STATUS.failed]: "danger",
  [PAYMENT_STATUS.cancelled]: "muted",
  [PAYMENT_STATUS.partially_refunded]: "warning",
  [PAYMENT_STATUS.refunded]: "muted",
} as const satisfies Record<keyof typeof PAYMENT_STATUS_LABELS, StatusTone>;

export const SHIPPING_STATUS_TONES = {
  [SHIPPING_STATUS.pending]: "warning",
  [SHIPPING_STATUS.preparing]: "info",
  [SHIPPING_STATUS.shipped]: "info",
  [SHIPPING_STATUS.in_transit]: "info",
  [SHIPPING_STATUS.delivered]: "success",
  [SHIPPING_STATUS.failed]: "danger",
  [SHIPPING_STATUS.returned]: "warning",
  [SHIPPING_STATUS.cancelled]: "muted",
} as const satisfies Record<keyof typeof SHIPPING_STATUS_LABELS, StatusTone>;

export const REVIEW_STATUS_TONES = {
  [REVIEW_STATUS.pending]: "warning",
  [REVIEW_STATUS.approved]: "success",
  [REVIEW_STATUS.rejected]: "danger",
  [REVIEW_STATUS.hidden]: "muted",
  [REVIEW_STATUS.cancelled]: "muted",
} as const satisfies Record<keyof typeof REVIEW_STATUS_LABELS, StatusTone>;

export const NOTIFICATION_STATUS_TONES = {
  [NOTIFICATION_STATUS.pending]: "warning",
  [NOTIFICATION_STATUS.unread]: "info",
  [NOTIFICATION_STATUS.read]: "success",
  [NOTIFICATION_STATUS.archived]: "muted",
  [NOTIFICATION_STATUS.cancelled]: "muted",
  [NOTIFICATION_STATUS.failed]: "danger",
} as const satisfies Record<keyof typeof NOTIFICATION_STATUS_LABELS, StatusTone>;

export const SNAPSHOT_PERIOD_TONES = {
  [SNAPSHOT_PERIOD.daily]: "info",
  [SNAPSHOT_PERIOD.weekly]: "warning",
  [SNAPSHOT_PERIOD.monthly]: "success",
} as const satisfies Record<keyof typeof SNAPSHOT_PERIOD_LABELS, StatusTone>;

export const ADMIN_ALERT_SEVERITY_TONES = {
  [ADMIN_ALERT_SEVERITY.critical]: "danger",
  [ADMIN_ALERT_SEVERITY.warning]: "warning",
  [ADMIN_ALERT_SEVERITY.info]: "info",
} as const satisfies Record<keyof typeof ADMIN_ALERT_SEVERITY_LABELS, StatusTone>;

function humanizeStatus(value: string): string {
  return value
    .replaceAll("_", " ")
    .replaceAll("-", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function getMappedLabel<T extends Record<string, string>>(
  labels: T,
  status: string,
): string {
  return labels[status as keyof T] ?? humanizeStatus(status);
}

function getMappedTone<T extends Record<string, StatusTone>>(
  tones: T,
  status: string,
): StatusTone {
  return tones[status as keyof T] ?? "default";
}

export function getOrderStatusLabel(status: string): string {
  return getMappedLabel(ORDER_STATUS_LABELS, status);
}

export function getPaymentStatusLabel(status: string): string {
  return getMappedLabel(PAYMENT_STATUS_LABELS, status);
}

export function getShippingStatusLabel(status: string): string {
  return getMappedLabel(SHIPPING_STATUS_LABELS, status);
}

export function getReviewStatusLabel(status: string): string {
  return getMappedLabel(REVIEW_STATUS_LABELS, status);
}

export function getNotificationStatusLabel(status: string): string {
  return getMappedLabel(NOTIFICATION_STATUS_LABELS, status);
}

export function getSnapshotPeriodLabel(period: string): string {
  return getMappedLabel(SNAPSHOT_PERIOD_LABELS, period);
}

export function getAdminAlertSeverityLabel(severity: string): string {
  return getMappedLabel(ADMIN_ALERT_SEVERITY_LABELS, severity);
}

export function getOrderStatusTone(status: string): StatusTone {
  return getMappedTone(ORDER_STATUS_TONES, status);
}

export function getPaymentStatusTone(status: string): StatusTone {
  return getMappedTone(PAYMENT_STATUS_TONES, status);
}

export function getShippingStatusTone(status: string): StatusTone {
  return getMappedTone(SHIPPING_STATUS_TONES, status);
}

export function getReviewStatusTone(status: string): StatusTone {
  return getMappedTone(REVIEW_STATUS_TONES, status);
}

export function getNotificationStatusTone(status: string): StatusTone {
  return getMappedTone(NOTIFICATION_STATUS_TONES, status);
}

export function getSnapshotPeriodTone(period: string): StatusTone {
  return getMappedTone(SNAPSHOT_PERIOD_TONES, period);
}

export function getAdminAlertSeverityTone(severity: string): StatusTone {
  return getMappedTone(ADMIN_ALERT_SEVERITY_TONES, severity);
}