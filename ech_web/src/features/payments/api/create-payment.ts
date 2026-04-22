import { apiClient } from "@/lib/api/client";
import { buildIdempotencyHeaders } from "@/lib/api/idempotency";

import type {
  CreatePaymentInput,
  PaymentDetail,
} from "@/features/payments/types/payment";

export async function createPayment(
  payload: CreatePaymentInput,
): Promise<PaymentDetail> {
  return apiClient.post<PaymentDetail>("/payments/create/", payload, {
    auth: true,
    headers: buildIdempotencyHeaders("payments-create"),
  });
}