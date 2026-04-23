"use client";

import { useState } from "react";

import { NotificationCard } from "./notification-card";
import { NotificationFilters } from "./notification-filters";
import { useNotifications } from "../hooks/use-notifications";
import type { ListNotificationsFilters } from "../api/list-notifications";

export function NotificationsList() {
  const [filters, setFilters] = useState<ListNotificationsFilters>({});
  const { data, isLoading, isError } = useNotifications(filters);

  if (isLoading) {
    return (
      <div className="py-10 text-center text-slate-400">
        Loading notifications...
      </div>
    );
  }

  if (isError) {
    return (
      <div className="py-10 text-center text-red-400">
        Unable to load notifications.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <NotificationFilters
        initialFilters={filters}
        onApply={setFilters}
      />

      {!data?.results.length ? (
        <div className="py-10 text-center text-slate-500">
          No notifications found.
        </div>
      ) : (
        <div className="grid gap-4">
          {data.results.map((notification) => (
            <NotificationCard
              key={notification.id}
              notification={notification}
            />
          ))}
        </div>
      )}
    </div>
  );
}