"use client";

import { useQuery } from "@tanstack/react-query";

import { listOrders, type ListOrdersFilters } from "@/features/orders/api/list-orders";
import { orderQueryKeys } from "@/features/orders/utils/order-query-keys";

export function useOrders(filters: ListOrdersFilters = {}) {
  return useQuery({
    queryKey: orderQueryKeys.list(filters),
    queryFn: () => listOrders(filters),
  });
}