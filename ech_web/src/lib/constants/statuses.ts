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
} as const;

export const REVIEW_STATUS = {
  pending: "pending",
  approved: "approved",
  rejected: "rejected",
  flagged: "flagged",
  archived: "archived",
} as const;

export const NOTIFICATION_STATUS = {
  pending: "pending",
  queued: "queued",
  dispatching: "dispatching",
  dispatched: "dispatched",
  delivered: "delivered",
  read: "read",
  archived: "archived",
  failed: "failed",
  cancelled: "cancelled",
} as const;

export const SNAPSHOT_STATUS = {
  pending: "pending",
  running: "running",
  completed: "completed",
  failed: "failed",
  cancelled: "cancelled",
} as const;

export const ADMIN_ALERT_STATUS = {
  open: "open",
  acknowledged: "acknowledged",
  resolved: "resolved",
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
} as const;

export const REVIEW_STATUS_LABELS = {
  [REVIEW_STATUS.pending]: "Pending",
  [REVIEW_STATUS.approved]: "Approved",
  [REVIEW_STATUS.rejected]: "Rejected",
  [REVIEW_STATUS.flagged]: "Flagged",
  [REVIEW_STATUS.archived]: "Archived",
} as const;

export const NOTIFICATION_STATUS_LABELS = {
  [NOTIFICATION_STATUS.pending]: "Pending",
  [NOTIFICATION_STATUS.queued]: "Queued",
  [NOTIFICATION_STATUS.dispatching]: "Dispatching",
  [NOTIFICATION_STATUS.dispatched]: "Dispatched",
  [NOTIFICATION_STATUS.delivered]: "Delivered",
  [NOTIFICATION_STATUS.read]: "Read",
  [NOTIFICATION_STATUS.archived]: "Archived",
  [NOTIFICATION_STATUS.failed]: "Failed",
  [NOTIFICATION_STATUS.cancelled]: "Cancelled",
} as const;

export const SNAPSHOT_STATUS_LABELS = {
  [SNAPSHOT_STATUS.pending]: "Pending",
  [SNAPSHOT_STATUS.running]: "Running",
  [SNAPSHOT_STATUS.completed]: "Completed",
  [SNAPSHOT_STATUS.failed]: "Failed",
  [SNAPSHOT_STATUS.cancelled]: "Cancelled",
} as const;

export const ADMIN_ALERT_STATUS_LABELS = {
  [ADMIN_ALERT_STATUS.open]: "Open",
  [ADMIN_ALERT_STATUS.acknowledged]: "Acknowledged",
  [ADMIN_ALERT_STATUS.resolved]: "Resolved",
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
} as const satisfies Record<keyof typeof SHIPPING_STATUS_LABELS, StatusTone>;

export const REVIEW_STATUS_TONES = {
  [REVIEW_STATUS.pending]: "warning",
  [REVIEW_STATUS.approved]: "success",
  [REVIEW_STATUS.rejected]: "danger",
  [REVIEW_STATUS.flagged]: "warning",
  [REVIEW_STATUS.archived]: "muted",
} as const satisfies Record<keyof typeof REVIEW_STATUS_LABELS, StatusTone>;

export const NOTIFICATION_STATUS_TONES = {
  [NOTIFICATION_STATUS.pending]: "warning",
  [NOTIFICATION_STATUS.queued]: "info",
  [NOTIFICATION_STATUS.dispatching]: "info",
  [NOTIFICATION_STATUS.dispatched]: "info",
  [NOTIFICATION_STATUS.delivered]: "success",
  [NOTIFICATION_STATUS.read]: "success",
  [NOTIFICATION_STATUS.archived]: "muted",
  [NOTIFICATION_STATUS.failed]: "danger",
  [NOTIFICATION_STATUS.cancelled]: "muted",
} as const satisfies Record<keyof typeof NOTIFICATION_STATUS_LABELS, StatusTone>;

export const SNAPSHOT_STATUS_TONES = {
  [SNAPSHOT_STATUS.pending]: "warning",
  [SNAPSHOT_STATUS.running]: "info",
  [SNAPSHOT_STATUS.completed]: "success",
  [SNAPSHOT_STATUS.failed]: "danger",
  [SNAPSHOT_STATUS.cancelled]: "muted",
} as const satisfies Record<keyof typeof SNAPSHOT_STATUS_LABELS, StatusTone>;

export const ADMIN_ALERT_STATUS_TONES = {
  [ADMIN_ALERT_STATUS.open]: "danger",
  [ADMIN_ALERT_STATUS.acknowledged]: "warning",
  [ADMIN_ALERT_STATUS.resolved]: "success",
} as const satisfies Record<keyof typeof ADMIN_ALERT_STATUS_LABELS, StatusTone>;

export function getOrderStatusLabel(status: keyof typeof ORDER_STATUS_LABELS): string {
  return ORDER_STATUS_LABELS[status];
}

export function getPaymentStatusLabel(
  status: keyof typeof PAYMENT_STATUS_LABELS,
): string {
  return PAYMENT_STATUS_LABELS[status];
}

export function getShippingStatusLabel(
  status: keyof typeof SHIPPING_STATUS_LABELS,
): string {
  return SHIPPING_STATUS_LABELS[status];
}

export function getReviewStatusLabel(status: keyof typeof REVIEW_STATUS_LABELS): string {
  return REVIEW_STATUS_LABELS[status];
}

export function getNotificationStatusLabel(
  status: keyof typeof NOTIFICATION_STATUS_LABELS,
): string {
  return NOTIFICATION_STATUS_LABELS[status];
}

export function getSnapshotStatusLabel(
  status: keyof typeof SNAPSHOT_STATUS_LABELS,
): string {
  return SNAPSHOT_STATUS_LABELS[status];
}

export function getAdminAlertStatusLabel(
  status: keyof typeof ADMIN_ALERT_STATUS_LABELS,
): string {
  return ADMIN_ALERT_STATUS_LABELS[status];
}

export function getOrderStatusTone(
  status: keyof typeof ORDER_STATUS_TONES,
): StatusTone {
  return ORDER_STATUS_TONES[status];
}

export function getPaymentStatusTone(
  status: keyof typeof PAYMENT_STATUS_TONES,
): StatusTone {
  return PAYMENT_STATUS_TONES[status];
}

export function getShippingStatusTone(
  status: keyof typeof SHIPPING_STATUS_TONES,
): StatusTone {
  return SHIPPING_STATUS_TONES[status];
}

export function getReviewStatusTone(
  status: keyof typeof REVIEW_STATUS_TONES,
): StatusTone {
  return REVIEW_STATUS_TONES[status];
}

export function getNotificationStatusTone(
  status: keyof typeof NOTIFICATION_STATUS_TONES,
): StatusTone {
  return NOTIFICATION_STATUS_TONES[status];
}

export function getSnapshotStatusTone(
  status: keyof typeof SNAPSHOT_STATUS_TONES,
): StatusTone {
  return SNAPSHOT_STATUS_TONES[status];
}

export function getAdminAlertStatusTone(
  status: keyof typeof ADMIN_ALERT_STATUS_TONES,
): StatusTone {
  return ADMIN_ALERT_STATUS_TONES[status];
}