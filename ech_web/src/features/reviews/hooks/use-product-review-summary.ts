"use client";

import { useQuery } from "@tanstack/react-query";

import { retrieveProductReviewSummary } from "@/features/reviews/api/retrieve-product-review-summary";
import { reviewQueryKeys } from "@/features/reviews/utils/review-query-keys";

export function useProductReviewSummary(productId?: string) {
  return useQuery({
    queryKey: reviewQueryKeys.productSummary(productId ?? ""),
    queryFn: () => {
      if (!productId) {
        throw new Error("Product id is required");
      }

      return retrieveProductReviewSummary(productId);
    },
    enabled: Boolean(productId),
  });
}