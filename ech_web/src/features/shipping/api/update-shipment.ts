import { apiClient } from "@/lib/api/client";

import type {
  ShipmentManagementDetail,
  UpdateShipmentInput,
} from "@/features/shipping/types/shipment";

export async function updateShipment(
  shipmentId: string,
  payload: UpdateShipmentInput,
): Promise<ShipmentManagementDetail> {
  return apiClient.patch<ShipmentManagementDetail>(
    `/shipping/${shipmentId}/update/`,
    payload,
    { auth: true },
  );
}