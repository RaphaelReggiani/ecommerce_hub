"use client";

import { useQuery } from "@tanstack/react-query";

import { listReviews } from "@/features/reviews/api/list-reviews";
import type { ReviewFiltersInput } from "@/features/reviews/types/review";
import { reviewQueryKeys } from "@/features/reviews/utils/review-query-keys";

export function useReviews(filters: ReviewFiltersInput = {}) {
  return useQuery({
    queryKey: reviewQueryKeys.list(filters),
    queryFn: () => listReviews(filters),
  });
}