import { apiClient } from "@/lib/api/client";
import { buildQueryString } from "@/lib/utils/build-query-string";
import type { PaginatedApiResponse } from "@/types/api";

import type {
  ProductPublicReview,
  ReviewFiltersInput,
} from "@/features/reviews/types/review";

export async function listProductReviews(
  productId: string,
  filters: ReviewFiltersInput = {},
): Promise<PaginatedApiResponse<ProductPublicReview>> {
  const queryString = buildQueryString(filters);

  return apiClient.get<PaginatedApiResponse<ProductPublicReview>>(
    `/reviews/product/${productId}/${queryString}`,
  );
}