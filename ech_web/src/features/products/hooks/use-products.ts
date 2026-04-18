"use client";

import { useQuery } from "@tanstack/react-query";

import { listProducts } from "@/features/products/api/list-products";
import type { ProductFiltersInput } from "@/features/products/types/product-filters";
import { productQueryKeys } from "@/features/products/utils/product-query-keys";

export function useProducts(filters: ProductFiltersInput = {}) {
  return useQuery({
    queryKey: productQueryKeys.list(filters),
    queryFn: () => listProducts(filters),
  });
}