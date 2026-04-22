"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createRefund } from "@/features/payments/api/create-refund";
import type { CreateRefundInput } from "@/features/payments/types/payment";
import { paymentQueryKeys } from "@/features/payments/utils/payment-query-keys";

export function useCreateRefund(paymentId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateRefundInput) =>
      createRefund(paymentId, payload),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: paymentQueryKeys.detail(paymentId),
      });
    },
  });
}