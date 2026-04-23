import { apiClient } from "@/lib/api/client";

import type {
  CancelReviewInput,
  ReviewDetail,
} from "@/features/reviews/types/review";

export async function cancelReview(
  reviewId: string,
  payload: CancelReviewInput = {},
): Promise<ReviewDetail> {
  return apiClient.post<ReviewDetail>(
    `/reviews/${reviewId}/cancel/`,
    payload,
    { auth: true },
  );
}