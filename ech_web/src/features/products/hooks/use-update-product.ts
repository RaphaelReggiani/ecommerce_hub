"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { updateProduct } from "@/features/products/api/update-product";
import type { ProductUpdateInput } from "@/features/products/types/product";
import { productQueryKeys } from "@/features/products/utils/product-query-keys";

type UpdateProductPayload = {
  productId: string;
  data: ProductUpdateInput;
};

export function useUpdateProduct() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ productId, data }: UpdateProductPayload) =>
      updateProduct(productId, data),
    onSuccess: (product) => {
      queryClient.invalidateQueries({ queryKey: productQueryKeys.all });
      queryClient.setQueryData(productQueryKeys.detail(product.id), product);
    },
  });
}