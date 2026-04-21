"use client";

import { useQuery } from "@tanstack/react-query";

import { retrieveOrder } from "@/features/orders/api/retrieve-order";
import { orderQueryKeys } from "@/features/orders/utils/order-query-keys";

export function useOrder(orderId: string) {
  return useQuery({
    queryKey: orderQueryKeys.detail(orderId),
    queryFn: () => retrieveOrder(orderId),
    enabled: Boolean(orderId),
  });
}