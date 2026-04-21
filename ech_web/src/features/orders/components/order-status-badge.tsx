import type { OrderStatus } from "@/features/orders/types/order";

type OrderStatusBadgeProps = {
  status: OrderStatus;
};

const statusMap: Record<OrderStatus, string> = {
  pending: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  confirmed: "bg-blue-500/15 text-blue-300 border-blue-500/30",
  processing: "bg-indigo-500/15 text-indigo-300 border-indigo-500/30",
  shipped: "bg-cyan-500/15 text-cyan-300 border-cyan-500/30",
  delivered: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  cancelled: "bg-red-500/15 text-red-300 border-red-500/30",
  refunded: "bg-fuchsia-500/15 text-fuchsia-300 border-fuchsia-500/30",
};

const labelMap: Record<OrderStatus, string> = {
  pending: "Pending",
  confirmed: "Confirmed",
  processing: "Processing",
  shipped: "Shipped",
  delivered: "Delivered",
  cancelled: "Cancelled",
  refunded: "Refunded",
};

export function OrderStatusBadge({ status }: OrderStatusBadgeProps) {
  return (
    <span
      className={`inline-flex rounded-full border px-3 py-1 text-xs font-medium ${statusMap[status]}`}
    >
      {labelMap[status]}
    </span>
  );
}