"use client";

import { useState } from "react";

import { cancelOrder } from "@/features/orders/api/cancel-order";
import { OrderStatusBadge } from "@/features/orders/components/order-status-badge";
import type { OrderDetail } from "@/features/orders/types/order";
import { formatCurrency } from "@/lib/utils/format-currency";
import { formatDateTime } from "@/lib/utils/format-date";

type OrderDetailCardProps = {
  order: OrderDetail;
};

export function OrderDetailCard({ order }: OrderDetailCardProps) {
  const [isCancelling, setIsCancelling] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function handleCancel() {
    try {
      setIsCancelling(true);
      setMessage(null);
      await cancelOrder(order.id);
      setMessage("Order cancelled successfully. Refresh the page to see updates.");
    } catch (error) {
      const text =
        error instanceof Error
          ? error.message
          : "Unable to cancel this order right now.";

      setMessage(text);
    } finally {
      setIsCancelling(false);
    }
  }

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
              Order detail
            </p>
            <h1 className="mt-2 text-3xl font-semibold text-white">
              Order {order.id.slice(0, 8)}...
            </h1>
            <p className="mt-2 text-sm text-slate-400">
              Created on {formatDateTime(order.created_at)}
            </p>
          </div>

          <OrderStatusBadge status={order.status} />
        </div>

        {message && (
          <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-slate-300">
            {message}
          </div>
        )}

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
              Payment
            </p>
            <p className="mt-2 text-lg font-semibold capitalize text-white">
              {order.payment_status.replaceAll("_", " ")}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
              Shipping
            </p>
            <p className="mt-2 text-lg font-semibold capitalize text-white">
              {order.shipping_status.replaceAll("_", " ")}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
              Grand total
            </p>
            <p className="mt-2 text-lg font-semibold text-blue-400">
              {formatCurrency(Number(order.totals?.grand_total ?? 0))}
            </p>
          </div>
        </div>

        {order.status === "pending" && (
          <div className="mt-6">
            <button
              type="button"
              onClick={handleCancel}
              disabled={isCancelling}
              className="rounded-2xl border border-red-500/30 bg-red-500/10 px-5 py-3 text-sm font-medium text-red-300 transition hover:bg-red-500/20 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isCancelling ? "Cancelling..." : "Cancel order"}
            </button>
          </div>
        )}
      </section>

      <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
        <div className="mb-6">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Items
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-white">
            Products in this order
          </h2>
        </div>

        <div className="space-y-4">
          {order.items.map((item) => (
            <div
              key={item.id}
              className="rounded-2xl border border-slate-800 bg-slate-950 p-4"
            >
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                    {item.brand_snapshot}
                  </p>
                  <h3 className="mt-1 text-lg font-semibold text-white">
                    {item.product_name_snapshot}
                  </h3>
                  <p className="mt-1 text-sm text-slate-400">
                    {item.product_type_snapshot}
                  </p>
                </div>

                <div className="text-right">
                  <p className="text-sm text-slate-400">
                    Qty: {item.quantity}
                  </p>
                  <p className="mt-1 text-base font-semibold text-blue-400">
                    {formatCurrency(Number(item.total_price))}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {order.address && (
        <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
          <div className="mb-6">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
              Address
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-white">
              Shipping address
            </h2>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4 text-sm leading-7 text-slate-300">
            <p className="font-medium text-white">{order.address.full_name}</p>
            <p>{order.address.address_line}</p>
            <p>
              {order.address.city}, {order.address.state}
            </p>
            <p>
              {order.address.country} - {order.address.postal_code}
            </p>
            {order.address.phone && <p>Phone: {order.address.phone}</p>}
          </div>
        </section>
      )}
    </div>
  );
}