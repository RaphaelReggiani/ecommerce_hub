"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { manageRefund } from "@/features/payments/api/manage-refund";
import type { ManageRefundInput } from "@/features/payments/types/payment";
import { paymentQueryKeys } from "@/features/payments/utils/payment-query-keys";

export function useManageRefund(refundId: string, paymentId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ManageRefundInput) =>
      manageRefund(refundId, payload),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: paymentQueryKeys.detail(paymentId),
      });
    },
  });
}