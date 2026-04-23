import { apiClient } from "@/lib/api/client";

import type {
  ModerateReviewInput,
  ReviewManagementDetail,
} from "@/features/reviews/types/review";

export async function moderateReview(
  reviewId: string,
  payload: ModerateReviewInput,
): Promise<ReviewManagementDetail> {
  return apiClient.post<ReviewManagementDetail>(
    `/reviews/${reviewId}/moderate/`,
    payload,
    { auth: true },
  );
}