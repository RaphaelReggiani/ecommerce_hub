"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createProduct } from "@/features/products/api/create-product";
import type { ProductCreateInput } from "@/features/products/types/product";
import { productQueryKeys } from "@/features/products/utils/product-query-keys";

export function useCreateProduct() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ProductCreateInput) => createProduct(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: productQueryKeys.all });
    },
  });
}