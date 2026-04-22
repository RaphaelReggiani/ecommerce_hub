import { apiClient } from "@/lib/api/client";

import type { CancelPaymentInput } from "@/features/payments/types/payment";
import type { PaymentOperationResponse } from "@/features/payments/api/process-payment";

export async function cancelPayment(
  paymentId: string,
  payload: CancelPaymentInput = {},
): Promise<PaymentOperationResponse> {
  return apiClient.post<PaymentOperationResponse>(
    `/payments/${paymentId}/cancel/`,
    payload,
    { auth: true },
  );
}