import { apiClient } from "@/lib/api/client";

import type { ProductReviewSummary } from "@/features/reviews/types/review";

export async function retrieveProductReviewSummary(
  productId: string,
): Promise<ProductReviewSummary> {
  return apiClient.get<ProductReviewSummary>(
    `/reviews/product/${productId}/summary/`,
  );
}