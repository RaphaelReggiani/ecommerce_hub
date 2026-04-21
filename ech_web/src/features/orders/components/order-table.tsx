"use client";

import Link from "next/link";

import { OrderStatusBadge } from "@/features/orders/components/order-status-badge";
import type { OrderListItem } from "@/features/orders/types/order";
import { formatCurrency } from "@/lib/utils/format-currency";
import { formatDateTime } from "@/lib/utils/format-date";

type OrderTableProps = {
  orders: OrderListItem[];
};

export function OrderTable({ orders }: OrderTableProps) {
  if (!orders.length) {
    return (
      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-10 text-center text-slate-400">
        No orders found.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-3xl border border-slate-800 bg-slate-900/70 shadow-xl">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-800">
          <thead className="bg-slate-950/70">
            <tr>
              <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                Order
              </th>
              <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                Status
              </th>
              <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                Payment
              </th>
              <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                Shipping
              </th>
              <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                Total
              </th>
              <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                Created
              </th>
              <th className="px-6 py-4 text-right text-xs uppercase tracking-[0.2em] text-slate-500">
                Action
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-800">
            {orders.map((order) => (
              <tr key={order.id} className="hover:bg-slate-950/40">
                <td className="px-6 py-4 text-sm text-white">
                  <div className="font-medium">{order.id.slice(0, 8)}...</div>
                  <div className="text-slate-500">{order.currency}</div>
                </td>

                <td className="px-6 py-4">
                  <OrderStatusBadge status={order.status} />
                </td>

                <td className="px-6 py-4 text-sm capitalize text-slate-300">
                  {order.payment_status.replaceAll("_", " ")}
                </td>

                <td className="px-6 py-4 text-sm capitalize text-slate-300">
                  {order.shipping_status.replaceAll("_", " ")}
                </td>

                <td className="px-6 py-4 text-sm font-medium text-blue-400">
                  {formatCurrency(Number(order.totals?.grand_total ?? 0))}
                </td>

                <td className="px-6 py-4 text-sm text-slate-400">
                  {formatDateTime(order.created_at)}
                </td>

                <td className="px-6 py-4 text-right">
                  <Link
                    href={`/account/orders/${order.id}`}
                    className="inline-flex rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-blue-500 hover:text-white"
                  >
                    View details
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}