import { apiClient } from "@/lib/api/client";

import type {
  ProcessShipmentInput,
  ShipmentManagementDetail,
} from "@/features/shipping/types/shipment";

export async function processShipment(
  shipmentId: string,
  payload: ProcessShipmentInput,
): Promise<ShipmentManagementDetail> {
  return apiClient.post<ShipmentManagementDetail>(
    `/shipping/${shipmentId}/process/`,
    payload,
    { auth: true },
  );
}