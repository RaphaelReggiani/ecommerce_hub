"use client";

import { useQuery } from "@tanstack/react-query";

import { retrieveProduct } from "@/features/products/api/retrieve-product";
import { productQueryKeys } from "@/features/products/utils/product-query-keys";

export function useProduct(productId?: string) {
  return useQuery({
    queryKey: productQueryKeys.detail(productId ?? ""),
    queryFn: () => retrieveProduct(productId as string),
    enabled: Boolean(productId),
  });
}