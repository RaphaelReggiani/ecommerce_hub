"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { processPayment } from "@/features/payments/api/process-payment";
import type {
  ProcessPaymentInput,
} from "@/features/payments/types/payment";
import { paymentQueryKeys } from "@/features/payments/utils/payment-query-keys";

export function useProcessPayment(paymentId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ProcessPaymentInput) =>
      processPayment(paymentId, payload),

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