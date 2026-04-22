import type { ShipmentLifecycle } from "@/features/shipping/types/shipment";
import { formatDateTime } from "@/lib/utils/format-date";

type ShipmentTimelineProps = {
  lifecycle: ShipmentLifecycle | null;
};

const timelineItems = [
  { key: "preparing_at", label: "Preparing" },
  { key: "ready_to_ship_at", label: "Ready to ship" },
  { key: "shipped_at", label: "Shipped" },
  { key: "in_transit_at", label: "In transit" },
  { key: "out_for_delivery_at", label: "Out for delivery" },
  { key: "delivered_at", label: "Delivered" },
  { key: "failed_at", label: "Failed" },
  { key: "returned_at", label: "Returned" },
  { key: "cancelled_at", label: "Cancelled" },
] as const;

export function ShipmentTimeline({ lifecycle }: ShipmentTimelineProps) {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
      <div className="mb-6">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
          Timeline
        </p>
        <h2 className="mt-2 text-2xl font-semibold text-white">
          Shipment lifecycle
        </h2>
      </div>

      <div className="space-y-4">
        {timelineItems.map((item) => {
          const value = lifecycle?.[item.key] ?? null;

          return (
            <div
              key={item.key}
              className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950 p-4"
            >
              <span className="text-sm font-medium text-slate-200">
                {item.label}
              </span>

              <span className="text-sm text-slate-400">
                {value ? formatDateTime(value) : "Not reached"}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}