import { cn } from "@/lib/utils/cn";
import type { NotificationStatus } from "@/features/notifications/types/notification";
import { getNotificationStatusLabel } from "@/features/notifications/utils/notification-mappers";

type Props = {
  status: NotificationStatus;
};

const statusStyles: Record<NotificationStatus, string> = {
  unread: "border-blue-500/30 bg-blue-500/10 text-blue-400",
  read: "border-slate-600 bg-slate-700/40 text-slate-300",
  archived: "border-purple-500/30 bg-purple-500/10 text-purple-400",
  failed: "border-red-500/30 bg-red-500/10 text-red-400",
  pending: "border-yellow-500/30 bg-yellow-500/10 text-yellow-400",
  cancelled: "border-slate-700 bg-slate-800/70 text-slate-400",
};

export function NotificationStatusBadge({ status }: Props) {
  return (
    <span
      className={cn(
        "rounded-full border px-2.5 py-0.5 text-xs font-medium",
        statusStyles[status],
      )}
    >
      {getNotificationStatusLabel(status)}
    </span>
  );
}