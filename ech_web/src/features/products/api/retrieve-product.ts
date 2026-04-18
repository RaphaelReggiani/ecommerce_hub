import { apiClient } from "@/lib/api/client";
import type { ProductDetail } from "@/features/products/types/product";

export async function retrieveProduct(productId: string): Promise<ProductDetail> {
  return apiClient.get<ProductDetail>(`/products/${productId}/`);
}