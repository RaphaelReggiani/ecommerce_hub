"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createOrder } from "@/features/orders/api/create-order";
import type { CreateOrderInput } from "@/features/orders/types/checkout";
import { orderQueryKeys } from "@/features/orders/utils/order-query-keys";

export function useCreateOrder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateOrderInput) => createOrder(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: orderQueryKeys.all });
    },
  });
}