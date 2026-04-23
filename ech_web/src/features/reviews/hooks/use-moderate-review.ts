"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { moderateReview } from "@/features/reviews/api/moderate-review";
import type { ModerateReviewInput } from "@/features/reviews/types/review";
import { reviewQueryKeys } from "@/features/reviews/utils/review-query-keys";

export function useModerateReview(reviewId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ModerateReviewInput) => moderateReview(reviewId, payload),
    onSuccess: (review) => {
      queryClient.invalidateQueries({ queryKey: reviewQueryKeys.managementDetail(reviewId) });
      queryClient.invalidateQueries({ queryKey: reviewQueryKeys.managementLists() });
      queryClient.invalidateQueries({ queryKey: reviewQueryKeys.productLists() });
      queryClient.invalidateQueries({
        queryKey: reviewQueryKeys.productSummary(review.product.id),
      });
    },
  });
}