import { apiClient } from "@/lib/api/client";
import type { PaginatedApiResponse } from "@/types/api";

import { buildQueryString } from "@/lib/utils/build-query-string";
import type { ProductFiltersInput } from "@/features/products/types/product-filters";
import type { ProductListItem } from "@/features/products/types/product";

export async function listProducts(
  filters: ProductFiltersInput = {},
): Promise<PaginatedApiResponse<ProductListItem>> {
  const queryString = buildQueryString(filters);

  return apiClient.get<PaginatedApiResponse<ProductListItem>>(
    `/products/list/${queryString}`,
  );
}