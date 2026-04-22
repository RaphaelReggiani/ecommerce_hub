"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { cancelPayment } from "@/features/payments/api/cancel-payment";
import type { CancelPaymentInput } from "@/features/payments/types/payment";
import { paymentQueryKeys } from "@/features/payments/utils/payment-query-keys";

export function useCancelPayment(paymentId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CancelPaymentInput = {}) =>
      cancelPayment(paymentId, payload),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: paymentQueryKeys.detail(paymentId),
      });

      queryClient.invalidateQueries({
        queryKey: paymentQueryKeys.lists(),
      });
    },
  });
}