import { apiClient } from "@/lib/api/client";

export async function deleteProduct(productId: string): Promise<void> {
  return apiClient.delete<void>(`/products/${productId}/delete/`, {
    auth: true,
  });
}