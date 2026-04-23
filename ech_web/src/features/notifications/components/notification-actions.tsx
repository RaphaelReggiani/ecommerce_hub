"use client";

import { useArchiveNotification } from "@/features/notifications/hooks/use-archive-notification";
import { useMarkNotificationAsRead } from "@/features/notifications/hooks/use-mark-notification-as-read";
import type { NotificationStatus } from "@/features/notifications/types/notification";
import {
  canArchiveNotification,
  canMarkNotificationAsRead,
} from "@/features/notifications/utils/notification-mappers";

type Props = {
  id: string;
  status: NotificationStatus;
};

export function NotificationActions({ id, status }: Props) {
  const markAsRead = useMarkNotificationAsRead();
  const archive = useArchiveNotification();

  const isPending = markAsRead.isPending || archive.isPending;

  return (
    <div className="flex gap-2">
      {canMarkNotificationAsRead(status) && (
        <button
          type="button"
          disabled={isPending}
          onClick={() => markAsRead.mutate(id)}
          className="text-xs text-blue-400 transition hover:text-blue-300 disabled:cursor-not-allowed disabled:opacity-60"
        >
          Mark as read
        </button>
      )}

      {canArchiveNotification(status) && (
        <button
          type="button"
          disabled={isPending}
          onClick={() => archive.mutate(id)}
          className="text-xs text-purple-400 transition hover:text-purple-300 disabled:cursor-not-allowed disabled:opacity-60"
        >
          Archive
        </button>
      )}
    </div>
  );
}