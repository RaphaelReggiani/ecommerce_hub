import type { ShipmentDetail } from "@/features/shipping/types/shipment";
import { formatCurrency } from "@/lib/utils/format-currency";
import { formatDateTime } from "@/lib/utils/format-date";

import { ShipmentStatusBadge } from "@/features/shipping/components/shipment-status-badge";

type ShipmentDetailCardProps = {
  shipment: ShipmentDetail;
};

export function ShipmentDetailCard({ shipment }: ShipmentDetailCardProps) {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
      <div className="mb-6 flex flex-col gap-4 border-b border-slate-800 pb-6 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Shipment
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-white">
            {shipment.id.slice(0, 8)}...
          </h2>
          <p className="mt-2 text-sm text-slate-400">
            Order: <span className="text-slate-200">{shipment.order}</span>
          </p>
        </div>

        <ShipmentStatusBadge status={shipment.status} />
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Method
          </p>
          <p className="mt-2 text-sm capitalize text-white">
            {shipment.shipping_method.replaceAll("_", " ")}
          </p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Carrier
          </p>
          <p className="mt-2 text-sm text-white">{shipment.carrier_name || "-"}</p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Tracking code
          </p>
          <p className="mt-2 text-sm text-white">{shipment.tracking_code || "-"}</p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            External reference
          </p>
          <p className="mt-2 text-sm text-white">
            {shipment.external_reference || "-"}
          </p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Shipping cost
          </p>
          <p className="mt-2 text-sm font-medium text-blue-400">
            {formatCurrency(Number(shipment.shipping_cost))}
          </p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Estimated delivery
          </p>
          <p className="mt-2 text-sm text-white">
            {shipment.estimated_delivery_date || "-"}
          </p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4 md:col-span-2 xl:col-span-3">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Delivery address
          </p>

          {shipment.address ? (
            <div className="mt-3 space-y-1 text-sm text-slate-200">
              <p>{shipment.address.full_name}</p>
              <p>{shipment.address.address_line}</p>
              <p>
                {shipment.address.city}, {shipment.address.state}
              </p>
              <p>
                {shipment.address.country} — {shipment.address.postal_code}
              </p>
              {shipment.address.phone ? <p>{shipment.address.phone}</p> : null}
              {shipment.address.delivery_instructions ? (
                <p className="pt-2 text-slate-400">
                  {shipment.address.delivery_instructions}
                </p>
              ) : null}
            </div>
          ) : (
            <p className="mt-2 text-sm text-slate-400">No address available.</p>
          )}
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4 md:col-span-2 xl:col-span-3">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Shipment metadata
          </p>
          <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <div>
              <p className="text-xs text-slate-500">Customer</p>
              <p className="mt-1 text-sm text-white">{shipment.customer_name}</p>
              <p className="text-xs text-slate-400">{shipment.customer_email}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Delivered to name</p>
              <p className="mt-1 text-sm text-white">
                {shipment.delivered_to_name || "-"}
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Return to sender</p>
              <p className="mt-1 text-sm text-white">
                {shipment.is_return_to_sender ? "Yes" : "No"}
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Created</p>
              <p className="mt-1 text-sm text-white">
                {formatDateTime(shipment.created_at)}
              </p>
              <p className="text-xs text-slate-400">
                Updated: {formatDateTime(shipment.updated_at)}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}