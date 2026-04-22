import { apiClient } from "@/lib/api/client";

import type {
  CancelShipmentInput,
  ShipmentManagementDetail,
} from "@/features/shipping/types/shipment";

export async function cancelShipment(
  shipmentId: string,
  payload: CancelShipmentInput = {},
): Promise<ShipmentManagementDetail> {
  return apiClient.post<ShipmentManagementDetail>(
    `/shipping/${shipmentId}/cancel/`,
    payload,
    { auth: true },
  );
}