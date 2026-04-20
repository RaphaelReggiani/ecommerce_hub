import { apiClient } from "@/lib/api/client";
import type { ProductDetail } from "@/features/products/types/product";

import { normalizeProductDetail } from "@/features/products/utils/product-mappers";

export async function retrieveProduct(
  productId: string,
): Promise<ProductDetail> {
  const product = await apiClient.get<ProductDetail>(`/products/${productId}/`);

  return normalizeProductDetail(product);
}