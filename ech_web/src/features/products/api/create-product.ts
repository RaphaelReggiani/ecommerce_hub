import { apiClient } from "@/lib/api/client";
import { buildIdempotencyHeaders } from "@/lib/api/idempotency";

import type {
  ProductCreateInput,
  ProductDetail,
} from "@/features/products/types/product";

export async function createProduct(
  payload: ProductCreateInput,
): Promise<ProductDetail> {
  return apiClient.post<ProductDetail>("/products/", payload, {
    auth: true,
    headers: buildIdempotencyHeaders("products-create"),
  });
}