"use client";

import { useQuery } from "@tanstack/react-query";

import { retrieveProduct } from "@/features/products/api/retrieve-product";
import { productQueryKeys } from "@/features/products/utils/product-query-keys";
import type { ProductDetail } from "@/features/products/types/product";

export function useProduct(productId?: string) {
  return useQuery<ProductDetail>({
    queryKey: productQueryKeys.detail(productId ?? ""),
    queryFn: async () => {
      if (!productId) {
        throw new Error("Product id is required");
      }

      return retrieveProduct(productId);
    },
    enabled: Boolean(productId),

    staleTime: 1000 * 60 * 5,

    refetchOnWindowFocus: false,
  });
}