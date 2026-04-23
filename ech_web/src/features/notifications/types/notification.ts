export type NotificationStatus =
  | "pending"
  | "unread"
  | "read"
  | "archived"
  | "cancelled"
  | "failed";

export type NotificationChannel =
  | "in_app"
  | "email"
  | "both";

export type NotificationPriority =
  | "low"
  | "normal"
  | "high"
  | "critical";

export type NotificationListItem = {
  id: string;
  recipient: number;
  recipient_name: string;
  recipient_email: string;
  channel: NotificationChannel;
  notification_type: string;
  title: string;
  priority: NotificationPriority;
  status: NotificationStatus;
  scheduled_for: string | null;
  created_at: string;
};

export type NotificationLifecycle = {
  dispatched_at: string | null;
  read_at: string | null;
  archived_at: string | null;
  cancelled_at: string | null;
  failed_at: string | null;
  created_at: string;
  updated_at: string;
};

export type NotificationEvent = {
  id: string;
  event_type: string;
  performed_by: number | null;
  performed_by_name: string | null;
  performed_by_email: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
};

export type NotificationDelivery = {
  id: string;
  channel: NotificationChannel;
  status: string;
  provider_name: string;
  recipient_address: string;
  external_message_id: string;
  failure_code: string;
  failure_message: string;
  metadata: Record<string, unknown> | null;
  performed_by: number | null;
  performed_by_name: string | null;
  performed_by_email: string | null;
  processed_at: string | null;
  created_at: string;
};

export type NotificationDetail = {
  id: string;
  recipient: number;
  recipient_name: string;
  recipient_email: string;
  channel: NotificationChannel;
  notification_type: string;
  title: string;
  message: string;
  priority: NotificationPriority;
  status: NotificationStatus;
  failure_code: string;
  failure_message: string;
  source_module: string;
  source_event: string;
  source_object_id: string;
  metadata: Record<string, unknown> | null;
  scheduled_for: string | null;
  lifecycle: NotificationLifecycle;
  events: NotificationEvent[];
  deliveries: NotificationDelivery[];
  created_at: string;
  updated_at: string;
};