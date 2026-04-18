import { apiClient } from "@/lib/api/client";

import type {
  ProductDetail,
  ProductUpdateInput,
} from "@/features/products/types/product";

export async function updateProduct(
  productId: string,
  payload: ProductUpdateInput,
): Promise<ProductDetail> {
  return apiClient.patch<ProductDetail>(
    `/products/${productId}/update/`,
    payload,
    { auth: true },
  );
}