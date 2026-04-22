import { apiClient } from "@/lib/api/client";
import { buildQueryString } from "@/lib/utils/build-query-string";
import type { PaginatedApiResponse } from "@/types/api";

import type {
  PaymentFiltersInput,
  PaymentListItem,
} from "@/features/payments/types/payment";

export async function listPayments(
  filters: PaymentFiltersInput = {},
): Promise<PaginatedApiResponse<PaymentListItem>> {
  const queryString = buildQueryString(filters);

  return apiClient.get<PaginatedApiResponse<PaymentListItem>>(
    `/payments/${queryString}`,
    { auth: true },
  );
}