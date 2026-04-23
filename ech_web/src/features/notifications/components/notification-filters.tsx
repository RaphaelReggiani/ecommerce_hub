"use client";

import { useState } from "react";

import type { ListNotificationsFilters } from "@/features/notifications/api/list-notifications";

type NotificationFiltersProps = {
  initialFilters?: ListNotificationsFilters;
  onApply: (filters: ListNotificationsFilters) => void;
};

export function NotificationFilters({
  initialFilters = {},
  onApply,
}: NotificationFiltersProps) {
  const [status, setStatus] = useState(initialFilters.status ?? "");
  const [channel, setChannel] = useState(initialFilters.channel ?? "");
  const [priority, setPriority] = useState(initialFilters.priority ?? "");

  function handleApply() {
    onApply({
      status: status || undefined,
      channel: channel || undefined,
      priority: priority || undefined,
    });
  }

  function handleClear() {
    setStatus("");
    setChannel("");
    setPriority("");
    onApply({});
  }

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-5 shadow-xl">
      <div className="grid gap-4 md:grid-cols-4">
        <select
          value={status}
          onChange={(event) => setStatus(event.target.value)}
          className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-500"
        >
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="unread">Unread</option>
          <option value="read">Read</option>
          <option value="archived">Archived</option>
          <option value="cancelled">Cancelled</option>
          <option value="failed">Failed</option>
        </select>

        <select
          value={channel}
          onChange={(event) => setChannel(event.target.value)}
          className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-500"
        >
          <option value="">All channels</option>
          <option value="in_app">In-app</option>
          <option value="email">Email</option>
          <option value="both">Both</option>
        </select>

        <select
          value={priority}
          onChange={(event) => setPriority(event.target.value)}
          className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-500"
        >
          <option value="">All priorities</option>
          <option value="low">Low</option>
          <option value="normal">Normal</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleApply}
            className="flex-1 rounded-2xl bg-blue-600 px-5 py-3 text-sm font-medium text-white transition hover:bg-blue-500"
          >
            Apply
          </button>

          <button
            type="button"
            onClick={handleClear}
            className="rounded-2xl border border-slate-700 px-5 py-3 text-sm font-medium text-slate-300 transition hover:border-slate-500 hover:text-white"
          >
            Clear
          </button>
        </div>
      </div>
    </div>
  );
}