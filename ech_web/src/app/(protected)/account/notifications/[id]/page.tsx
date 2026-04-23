// src/app/(protected)/account/notifications/[id]/page.tsx

"use client";

import { useParams } from "next/navigation";

import { useNotification } from "@/features/notifications/hooks/use-notification";
import { NotificationStatusBadge } from "@/features/notifications/components/notification-status-badge";
import { formatDate } from "@/lib/utils/format-date";

export default function NotificationDetailPage() {
  const params = useParams();
  const id = typeof params.id === "string" ? params.id : "";

  const { data, isLoading, isError } = useNotification(id);

  if (isLoading) {
    return (
      <div className="text-center text-slate-400 py-10">
        Loading notification...
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="text-center text-red-400 py-10">
        Unable to load notification.
      </div>
    );
  }

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-8 shadow-xl">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-white">
          {data.title}
        </h1>

        <NotificationStatusBadge status={data.status} />
      </div>

      <p className="mt-4 text-slate-300">{data.message}</p>

      <div className="mt-6 text-sm text-slate-500">
        Created at: {formatDate(data.created_at)}
      </div>
    </div>
  );
}