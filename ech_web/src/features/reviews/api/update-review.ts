import { apiClient } from "@/lib/api/client";

import type {
  ReviewDetail,
  UpdateReviewInput,
} from "@/features/reviews/types/review";

export async function updateReview(
  reviewId: string,
  payload: UpdateReviewInput,
): Promise<ReviewDetail> {
  return apiClient.patch<ReviewDetail>(
    `/reviews/${reviewId}/update/`,
    payload,
    { auth: true },
  );
}