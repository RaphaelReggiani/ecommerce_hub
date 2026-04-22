import { apiClient } from "@/lib/api/client";

import type { ManageRefundInput } from "@/features/payments/types/payment";
import type { RefundOperationResponse } from "@/features/payments/api/create-refund";

export async function manageRefund(
  refundId: string,
  payload: ManageRefundInput,
): Promise<RefundOperationResponse> {
  return apiClient.post<RefundOperationResponse>(
    `/payments/refund/${refundId}/manage/`,
    payload,
    { auth: true },
  );
}