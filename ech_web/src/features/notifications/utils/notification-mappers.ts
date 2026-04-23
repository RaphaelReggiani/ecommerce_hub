import type {
  NotificationPriority,
  NotificationStatus,
} from "@/features/notifications/types/notification";

export function getNotificationStatusLabel(status: NotificationStatus): string {
  const labels: Record<NotificationStatus, string> = {
    pending: "Pending",
    unread: "Unread",
    read: "Read",
    archived: "Archived",
    cancelled: "Cancelled",
    failed: "Failed",
  };

  return labels[status];
}

export function getNotificationPriorityLabel(
  priority: NotificationPriority,
): string {
  const labels: Record<NotificationPriority, string> = {
    low: "Low",
    normal: "Normal",
    high: "High",
    critical: "Critical",
  };

  return labels[priority];
}

export function canMarkNotificationAsRead(status: NotificationStatus): boolean {
  return status === "unread" || status === "pending";
}

export function canArchiveNotification(status: NotificationStatus): boolean {
  return status !== "archived" && status !== "cancelled";
}

export function isNotificationUnread(status: NotificationStatus): boolean {
  return status === "unread";
}

export function getNotificationErrorMessage(message: string): string {
  const normalized = message.toLowerCase();

  if (normalized.includes("already marked as read")) {
    return "This notification is already marked as read.";
  }

  if (normalized.includes("already archived")) {
    return "This notification is already archived.";
  }

  if (normalized.includes("not found")) {
    return "Notification not found.";
  }

  if (normalized.includes("permission")) {
    return "You do not have permission to access this notification.";
  }

  if (normalized.includes("invalid notification operation")) {
    return "This notification action is not allowed.";
  }

  if (normalized.includes("invalid notification state")) {
    return "This notification cannot be moved to that state.";
  }

  return message;
}