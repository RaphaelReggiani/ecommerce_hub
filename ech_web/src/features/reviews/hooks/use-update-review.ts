"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { updateReview } from "@/features/reviews/api/update-review";
import type { UpdateReviewInput } from "@/features/reviews/types/review";
import { reviewQueryKeys } from "@/features/reviews/utils/review-query-keys";

export function useUpdateReview(reviewId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: UpdateReviewInput) => updateReview(reviewId, payload),
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