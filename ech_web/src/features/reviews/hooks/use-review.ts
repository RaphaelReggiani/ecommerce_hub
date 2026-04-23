"use client";

import { useQuery } from "@tanstack/react-query";

import { retrieveReview } from "@/features/reviews/api/retrieve-review";
import { reviewQueryKeys } from "@/features/reviews/utils/review-query-keys";

export function useReview(reviewId?: string) {
  return useQuery({
    queryKey: reviewQueryKeys.detail(reviewId ?? ""),
    queryFn: () => {
      if (!reviewId) {
        throw new Error("Review id is required");
      }

      return retrieveReview(reviewId);
    },
    enabled: Boolean(reviewId),
  });
}