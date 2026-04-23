import { apiClient } from "@/lib/api/client";
import { buildQueryString } from "@/lib/utils/build-query-string";
import type { PaginatedApiResponse } from "@/types/api";

import type {
  ReviewFiltersInput,
  ReviewListItem,
} from "@/features/reviews/types/review";

export async function listReviews(
  filters: ReviewFiltersInput = {},
): Promise<PaginatedApiResponse<ReviewListItem>> {
  const queryString = buildQueryString(filters);

  return apiClient.get<PaginatedApiResponse<ReviewListItem>>(
    `/reviews/${queryString}`,
    { auth: true },
  );
}