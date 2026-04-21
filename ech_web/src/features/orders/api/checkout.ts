import type { CreateOrderInput } from "@/features/orders/types/checkout";
import type { OrderDetail } from "@/features/orders/types/order";
import { createOrder } from "@/features/orders/api/create-order";

export async function checkout(payload: CreateOrderInput): Promise<OrderDetail> {
  return createOrder(payload);
}