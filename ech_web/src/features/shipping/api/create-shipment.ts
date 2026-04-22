import { apiClient } from "@/lib/api/client";
import {
  buildIdempotencyHeaders,
  generateIdempotencyKey,
} from "@/lib/api/idempotency";

import type {
  CreateShipmentInput,
  ShipmentManagementDetail,
} from "@/features/shipping/types/shipment";

export async function createShipment(
  payload: CreateShipmentInput,
): Promise<ShipmentManagementDetail> {
  const idempotencyKey = payload.idempotency_key ?? generateIdempotencyKey("shipping-create");

  return apiClient.post<ShipmentManagementDetail>(
    "/shipping/create/",
    {
      ...payload,
      idempotency_key: idempotencyKey,
    },
    {
      auth: true,
      headers: buildIdempotencyHeaders("shipping-create"),
    },
  );
}