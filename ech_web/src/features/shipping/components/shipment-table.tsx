"use client";

import Link from "next/link";

import { EmptyState } from "@/components/feedback/empty-state";
import { routes } from "@/config/routes";
import { ShipmentStatusBadge } from "@/features/shipping/components/shipment-status-badge";
import type { ShipmentListItem } from "@/features/shipping/types/shipment";
import { formatCurrency } from "@/lib/utils/format-currency";
import { formatDateTime } from "@/lib/utils/format-date";

type ShipmentTableProps = {
  shipments: ShipmentListItem[];
};

export function ShipmentTable({ shipments }: ShipmentTableProps) {
  if (!shipments.length) {
    return (
      <EmptyState
        title="No shipments found."
        description="There are no shipment records available for your account yet."
      />
    );
  }

  return (
    <div className="overflow-hidden rounded-3xl border border-slate-800 bg-slate-900/70 shadow-xl">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-800">
          <thead className="bg-slate-950/70">
            <tr>
              <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                Shipment
              </th>
              <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                Status
              </th>
              <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                Method
              </th>
              <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                Carrier
              </th>
              <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                Tracking
              </th>
              <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                Shipping cost
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
            {shipments.map((shipment) => (
              <tr key={shipment.id} className="hover:bg-slate-950/40">
                <td className="px-6 py-4 text-sm text-white">
                  <div className="font-medium">{shipment.id.slice(0, 8)}...</div>
                  <div className="text-slate-500">Order {shipment.order}</div>
                </td>

                <td className="px-6 py-4">
                  <ShipmentStatusBadge status={shipment.status} />
                </td>

                <td className="px-6 py-4 text-sm capitalize text-slate-300">
                  {shipment.shipping_method.replaceAll("_", " ")}
                </td>

                <td className="px-6 py-4 text-sm text-slate-300">
                  {shipment.carrier_name || "-"}
                </td>

                <td className="px-6 py-4 text-sm text-slate-400">
                  {shipment.tracking_code || "-"}
                </td>

                <td className="px-6 py-4 text-sm font-medium text-blue-400">
                  {formatCurrency(Number(shipment.shipping_cost))}
                </td>

                <td className="px-6 py-4 text-sm text-slate-400">
                  {formatDateTime(shipment.created_at)}
                </td>

                <td className="px-6 py-4 text-right">
                  <Link
                    href={routes.protected.shipmentDetail(shipment.id)}
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