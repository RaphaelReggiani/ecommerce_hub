import Link from "next/link";

import type { NotificationListItem } from "@/features/notifications/types/notification";
import { NotificationStatusBadge } from "@/features/notifications/components/notification-status-badge";
import { NotificationActions } from "@/features/notifications/components/notification-actions";
import { formatDateTime } from "@/lib/utils/format-date";
import {
  getNotificationPriorityLabel,
  isNotificationUnread,
} from "@/features/notifications/utils/notification-mappers";

type Props = {
  notification: NotificationListItem;
};

export function NotificationCard({ notification }: Props) {
  const unread = isNotificationUnread(notification.status);

  return (
    <div
      className={`rounded-2xl border p-5 shadow-lg transition ${
        unread
          ? "border-blue-500/30 bg-blue-500/5"
          : "border-slate-800 bg-slate-900/70"
      }`}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-sm font-semibold text-white">
            {notification.title}
          </h3>

          <p className="mt-2 text-sm text-slate-400">
            {notification.notification_type}
          </p>

          <p className="mt-2 text-xs uppercase tracking-[0.18em] text-slate-500">
            {getNotificationPriorityLabel(notification.priority)} priority
          </p>

          <p className="mt-2 text-xs text-slate-500">
            {formatDateTime(notification.created_at)}
          </p>
        </div>

        <NotificationStatusBadge status={notification.status} />
      </div>

      <div className="mt-4 flex items-center justify-between gap-4">
        <Link
          href={`/account/notifications/${notification.id}`}
          className="text-xs text-blue-400 transition hover:text-blue-300"
        >
          View details
        </Link>

        <NotificationActions
          id={notification.id}
          status={notification.status}
        />
      </div>
    </div>
  );
}