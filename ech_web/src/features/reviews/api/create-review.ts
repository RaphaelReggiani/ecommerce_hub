import { apiClient } from "@/lib/api/client";
import {
  buildIdempotencyHeaders,
  generateIdempotencyKey,
} from "@/lib/api/idempotency";

import type {
  CreateReviewInput,
  ReviewDetail,
} from "@/features/reviews/types/review";

export async function createReview(
  payload: CreateReviewInput,
): Promise<ReviewDetail> {
  const idempotencyKey = payload.idempotency_key ?? generateIdempotencyKey("review-create");

  return apiClient.post<ReviewDetail>(
    "/reviews/create/",
    {
      ...payload,
      idempotency_key: idempotencyKey,
    },
    {
      auth: true,
      headers: buildIdempotencyHeaders("review-create"),
    },
  );
}