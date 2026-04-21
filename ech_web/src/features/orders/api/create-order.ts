import { apiClient } from "@/lib/api/client";
import { buildIdempotencyHeaders } from "@/lib/api/idempotency";

import type { OrderDetail } from "@/features/orders/types/order";
import type { CreateOrderInput } from "@/features/orders/types/checkout";

export async function createOrder(
  payload: CreateOrderInput,
): Promise<OrderDetail> {
  return apiClient.post<OrderDetail>("/orders/create/", payload, {
    headers: buildIdempotencyHeaders("orders-create"),
  });
}