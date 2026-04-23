"use client";

import { useQuery } from "@tanstack/react-query";

import { listProductReviews } from "@/features/reviews/api/list-product-reviews";
import type { ReviewFiltersInput } from "@/features/reviews/types/review";
import { reviewQueryKeys } from "@/features/reviews/utils/review-query-keys";

export function useProductReviews(
  productId?: string,
  filters: ReviewFiltersInput = {},
) {
  return useQuery({
    queryKey: reviewQueryKeys.productList(productId ?? "", filters),
    queryFn: () => {
      if (!productId) {
        throw new Error("Product id is required");
      }

      return listProductReviews(productId, filters);
    },
    enabled: Boolean(productId),
  });
}