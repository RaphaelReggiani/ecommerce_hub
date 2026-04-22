import { apiClient } from "@/lib/api/client";

import type { ProcessPaymentInput } from "@/features/payments/types/payment";

export type PaymentOperationResponse = {
  detail: string;
};

export async function processPayment(
  paymentId: string,
  payload: ProcessPaymentInput,
): Promise<PaymentOperationResponse> {
  return apiClient.post<PaymentOperationResponse>(
    `/payments/${paymentId}/process/`,
    payload,
    { auth: true },
  );
}