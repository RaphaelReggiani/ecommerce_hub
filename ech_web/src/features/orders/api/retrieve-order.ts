import { apiClient } from "@/lib/api/client";
import type { OrderDetail } from "@/features/orders/types/order";

export async function retrieveOrder(orderId: string): Promise<OrderDetail> {
  return apiClient.get<OrderDetail>(`/orders/${orderId}/`);
}