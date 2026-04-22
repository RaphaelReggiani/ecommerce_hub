import { apiClient } from "@/lib/api/client";

import type {
  ShipmentManagementDetail,
  TrackShipmentInput,
} from "@/features/shipping/types/shipment";

export async function trackShipment(
  shipmentId: string,
  payload: TrackShipmentInput,
): Promise<ShipmentManagementDetail> {
  return apiClient.post<ShipmentManagementDetail>(
    `/shipping/${shipmentId}/tracking/`,
    payload,
    { auth: true },
  );
}