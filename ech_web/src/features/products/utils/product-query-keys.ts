import type { ProductFiltersInput } from "@/features/products/types/product-filters";

export const productQueryKeys = {
  all: ["products"] as const,

  lists: () => [...productQueryKeys.all, "list"] as const,

  list: (filters: ProductFiltersInput = {}) =>
    [...productQueryKeys.lists(), filters] as const,

  details: () => [...productQueryKeys.all, "detail"] as const,

  detail: (productId: string) =>
    [...productQueryKeys.details(), productId] as const,
};