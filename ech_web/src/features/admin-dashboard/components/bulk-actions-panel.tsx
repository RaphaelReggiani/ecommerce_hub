"use client";

import { useState } from "react";

import { useAdminBulkActions } from "@/features/admin-dashboard/hooks/use-admin-bulk-actions";

export function BulkActionsPanel() {
  const { bulkOrderAction, bulkReviewModeration, bulkNotificationRetry, isPending } =
    useAdminBulkActions();

  const [orderIds, setOrderIds] = useState("");
  const [reviewIds, setReviewIds] = useState("");
  const [notificationIds, setNotificationIds] = useState("");

  const parseIds = (value: string) =>
    value
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
      <h2 className="text-xl font-semibold text-white">Bulk Actions</h2>
      <p className="mt-2 text-sm text-slate-400">
        Execute controlled administrative operations. Use comma-separated UUIDs.
      </p>

      <div className="mt-6 grid gap-5 xl:grid-cols-3">
        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <h3 className="font-medium text-white">Orders</h3>
          <textarea
            value={orderIds}
            onChange={(event) => setOrderIds(event.target.value)}
            placeholder="order-id-1, order-id-2"
            className="mt-3 min-h-28 w-full rounded-2xl border border-slate-700 bg-black px-4 py-3 text-sm text-white outline-none focus:border-blue-500"
          />
          <button
            type="button"
            disabled={isPending}
            onClick={() =>
              bulkOrderAction.mutate({
                action_type: "cancel",
                order_ids: parseIds(orderIds),
              })
            }
            className="mt-3 w-full rounded-2xl bg-blue-600 px-4 py-3 text-sm font-medium text-white transition hover:bg-blue-500 disabled:opacity-50"
          >
            Cancel Orders
          </button>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <h3 className="font-medium text-white">Reviews</h3>
          <textarea
            value={reviewIds}
            onChange={(event) => setReviewIds(event.target.value)}
            placeholder="review-id-1, review-id-2"
            className="mt-3 min-h-28 w-full rounded-2xl border border-slate-700 bg-black px-4 py-3 text-sm text-white outline-none focus:border-blue-500"
          />
          <button
            type="button"
            disabled={isPending}
            onClick={() =>
              bulkReviewModeration.mutate({
                moderation_action: "hide",
                review_ids: parseIds(reviewIds),
                reason: "Bulk moderation from admin dashboard.",
              })
            }
            className="mt-3 w-full rounded-2xl bg-blue-600 px-4 py-3 text-sm font-medium text-white transition hover:bg-blue-500 disabled:opacity-50"
          >
            Hide Reviews
          </button>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <h3 className="font-medium text-white">Notifications</h3>
          <textarea
            value={notificationIds}
            onChange={(event) => setNotificationIds(event.target.value)}
            placeholder="notification-id-1, notification-id-2"
            className="mt-3 min-h-28 w-full rounded-2xl border border-slate-700 bg-black px-4 py-3 text-sm text-white outline-none focus:border-blue-500"
          />
          <button
            type="button"
            disabled={isPending}
            onClick={() =>
              bulkNotificationRetry.mutate({
                notification_ids: parseIds(notificationIds),
              })
            }
            className="mt-3 w-full rounded-2xl bg-blue-600 px-4 py-3 text-sm font-medium text-white transition hover:bg-blue-500 disabled:opacity-50"
          >
            Retry Notifications
          </button>
        </div>
      </div>
    </div>
  );
}