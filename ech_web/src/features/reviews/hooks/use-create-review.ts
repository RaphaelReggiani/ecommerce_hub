"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createReview } from "@/features/reviews/api/create-review";
import type { CreateReviewInput } from "@/features/reviews/types/review";
import { reviewQueryKeys } from "@/features/reviews/utils/review-query-keys";

export function useCreateReview() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateReviewInput) => createReview(payload),
    onSuccess: (review) => {
      queryClient.invalidateQueries({ queryKey: reviewQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: reviewQueryKeys.productLists() });
      queryClient.invalidateQueries({
        queryKey: reviewQueryKeys.productSummary(review.product.id),
      });
    },
  });
}