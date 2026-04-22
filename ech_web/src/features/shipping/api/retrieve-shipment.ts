import { apiClient } from "@/lib/api/client";

import type { ShipmentDetail } from "@/features/shipping/types/shipment";

export async function retrieveShipment(shipmentId: string): Promise<ShipmentDetail> {
  return apiClient.get<ShipmentDetail>(`/shipping/${shipmentId}/`, {
    auth: true,
  });
}