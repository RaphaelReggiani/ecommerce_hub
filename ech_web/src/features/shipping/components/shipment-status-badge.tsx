import { StatusBadge } from "@/components/shared/status-badge";
import type { StatusTone } from "@/lib/constants/statuses";

import type { ShipmentStatus } from "@/features/shipping/types/shipment";

type ShipmentStatusBadgeProps = {
  status: ShipmentStatus;
};

const statusLabels: Record<ShipmentStatus, string> = {
  pending: "Pending",
  preparing: "Preparing",
  ready_to_ship: "Ready to ship",
  shipped: "Shipped",
  in_transit: "In transit",
  out_for_delivery: "Out for delivery",
  delivered: "Delivered",
  failed: "Failed",
  returned: "Returned",
  cancelled: "Cancelled",
};

const statusTones: Record<ShipmentStatus, StatusTone> = {
  pending: "warning",
  preparing: "info",
  ready_to_ship: "info",
  shipped: "info",
  in_transit: "info",
  out_for_delivery: "info",
  delivered: "success",
  failed: "danger",
  returned: "muted",
  cancelled: "muted",
};

export function ShipmentStatusBadge({ status }: ShipmentStatusBadgeProps) {
  return <StatusBadge tone={statusTones[status]}>{statusLabels[status]}</StatusBadge>;
}