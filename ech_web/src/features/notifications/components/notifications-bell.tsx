"use client";

import Link from "next/link";

import { useNotifications } from "@/features/notifications/hooks/use-notifications";
import { useAuth } from "@/providers/auth-provider";

export function NotificationsBell() {
  const { isAuthenticated } = useAuth();

  const { data } = useNotifications(
    { status: "unread" },
    { enabled: isAuthenticated },
  );

  if (!isAuthenticated) {
    return null;
  }

  const unreadCount = data?.results?.length ?? 0;

  return (
    <Link
      href="/account/notifications"
      className="relative inline-flex items-center justify-center rounded-xl border border-slate-700 bg-slate-950 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-blue-500 hover:text-white"
      aria-label="Notifications"
    >
      <span>Notifications</span>

      {unreadCount > 0 && (
        <span className="absolute -right-2 -top-2 inline-flex min-w-6 items-center justify-center rounded-full bg-blue-600 px-2 py-0.5 text-xs font-semibold text-white">
          {unreadCount > 99 ? "99+" : unreadCount}
        </span>
      )}
    </Link>
  );
}