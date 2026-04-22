import { apiClient } from "@/lib/api/client";

import type { CreateRefundInput } from "@/features/payments/types/payment";

export type RefundOperationResponse = {
  detail: string;
};

export async function createRefund(
  paymentId: string,
  payload: CreateRefundInput,
): Promise<RefundOperationResponse> {
  return apiClient.post<RefundOperationResponse>(
    `/payments/${paymentId}/refund/`,
    payload,
    { auth: true },
  );
}