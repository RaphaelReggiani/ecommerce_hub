import type { OrderLifecycle } from "@/features/orders/types/order";
import { formatDateTime } from "@/lib/utils/format-date";

type OrderTimelineProps = {
  lifecycle: OrderLifecycle | null;
};

const timelineItems = [
  { key: "confirmed_at", label: "Confirmed" },
  { key: "processing_at", label: "Processing started" },
  { key: "shipped_at", label: "Shipped" },
  { key: "delivered_at", label: "Delivered" },
  { key: "cancelled_at", label: "Cancelled" },
  { key: "refunded_at", label: "Refunded" },
] as const;

export function OrderTimeline({ lifecycle }: OrderTimelineProps) {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
      <div className="mb-6">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
          Timeline
        </p>
        <h2 className="mt-2 text-2xl font-semibold text-white">
          Order lifecycle
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