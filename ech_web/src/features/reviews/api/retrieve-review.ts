import { apiClient } from "@/lib/api/client";

import type { ReviewDetail } from "@/features/reviews/types/review";

export async function retrieveReview(reviewId: string): Promise<ReviewDetail> {
  return apiClient.get<ReviewDetail>(`/reviews/${reviewId}/`, {
    auth: true,
  });
}