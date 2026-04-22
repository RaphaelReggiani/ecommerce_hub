import type {
  ShipmentDetail,
  ShipmentListItem,
  ShipmentStatus,
} from "@/features/shipping/types/shipment";

export function canCancelShipment(status: ShipmentStatus): boolean {
  return !["delivered", "cancelled", "returned"].includes(status);
}

export function canProcessShipment(status: ShipmentStatus): boolean {
  return !["delivered", "cancelled", "returned"].includes(status);
}

export function hasTrackingCode(
  shipment: Pick<ShipmentListItem, "tracking_code">,
): boolean {
  return Boolean(shipment.tracking_code && shipment.tracking_code.trim());
}

export function getShipmentDisplayTrackingCode(
  shipment: Pick<ShipmentListItem, "tracking_code">,
): string {
  return shipment.tracking_code?.trim() || "-";
}

export function getLatestTrackingUpdate(shipment: ShipmentDetail) {
  return shipment.tracking_updates[0] ?? null;
}