"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { cancelReview } from "@/features/reviews/api/cancel-review";
import type { CancelReviewInput } from "@/features/reviews/types/review";
import { reviewQueryKeys } from "@/features/reviews/utils/review-query-keys";

export function useCancelReview(reviewId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CancelReviewInput = {}) => cancelReview(reviewId, payload),
    onSuccess: (review) => {
      queryClient.invalidateQueries({ queryKey: reviewQueryKeys.detail(reviewId) });
      queryClient.invalidateQueries({ queryKey: reviewQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: reviewQueryKeys.productLists() });
      queryClient.invalidateQueries({
        queryKey: reviewQueryKeys.productSummary(review.product.id),
      });
    },
  });
}