import { apiClient } from "@/lib/api/client";

import type { PaymentDetail } from "@/features/payments/types/payment";

export async function retrievePayment(paymentId: string): Promise<PaymentDetail> {
  return apiClient.get<PaymentDetail>(`/payments/${paymentId}/`, {
    auth: true,
  });
}