import { apiClient } from "@/lib/api/client";

import type { OrderDetail } from "@/features/orders/types/order";

export async function cancelOrder(orderId: string): Promise<OrderDetail> {
  return apiClient.post<OrderDetail>(`/orders/${orderId}/cancel/`, {});
}