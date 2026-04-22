"use client";

import { useMemo, useState } from "react";

import { ConfirmActionDialog } from "@/components/shared/confirm-action-dialog";
import { useCancelPayment } from "@/features/payments/hooks/use-cancel-payment";
import { useCreateRefund } from "@/features/payments/hooks/use-create-refund";
import { useProcessPayment } from "@/features/payments/hooks/use-process-payment";
import type {
  PaymentDetail,
  PaymentProcessAction,
} from "@/features/payments/types/payment";
import {
  canCancelPayment,
  canRefundPayment,
} from "@/features/payments/utils/payment-mappers";
import { ApiClientError } from "@/lib/api/error-handler";

type PaymentActionsProps = {
  payment: PaymentDetail;
};

export function PaymentActions({ payment }: PaymentActionsProps) {
  const processMutation = useProcessPayment(payment.id);
  const cancelMutation = useCancelPayment(payment.id);
  const refundMutation = useCreateRefund(payment.id);

  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedAction, setSelectedAction] = useState<
    PaymentProcessAction | "cancel" | "refund" | null
  >(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const canShowRefund = useMemo(() => canRefundPayment(payment), [payment]);
  const canShowCancel = useMemo(() => canCancelPayment(payment.status), [payment.status]);
  const canShowProcess = payment.status === "pending" || payment.status === "processing";
  const canShowCapture = payment.status === "processing" || payment.status === "authorized";
  const canShowFail = payment.status === "pending" || payment.status === "processing";

  function openAction(action: PaymentProcessAction | "cancel" | "refund") {
    setActionError(null);
    setSelectedAction(action);
    setDialogOpen(true);
  }

  function closeDialog() {
    setDialogOpen(false);
    setSelectedAction(null);
  }

  async function handleConfirm() {
    if (!selectedAction) {
      return;
    }

    setActionError(null);

    try {
      if (selectedAction === "cancel") {
        await cancelMutation.mutateAsync({});
      } else if (selectedAction === "refund") {
        const remainingAmount = (
          Number(payment.amount) - Number(payment.refunded_amount)
        ).toFixed(2);

        await refundMutation.mutateAsync({
          amount: remainingAmount,
          reason: "Requested from payment actions",
        });
      } else {
        await processMutation.mutateAsync({
          action: selectedAction,
        });
      }

      closeDialog();
    } catch (error) {
      if (error instanceof ApiClientError) {
        setActionError(error.message);
        return;
      }

      setActionError("Unable to complete this payment action right now.");
    }
  }

  const isPending =
    processMutation.isPending ||
    cancelMutation.isPending ||
    refundMutation.isPending;

  return (
    <>
      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
        <div className="mb-4">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Actions
          </p>
          <h3 className="mt-2 text-xl font-semibold text-white">
            Payment operations
          </h3>
        </div>

        {actionError ? (
          <div className="mb-4 rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            {actionError}
          </div>
        ) : null}

        <div className="flex flex-wrap gap-3">
          {canShowProcess && (
            <button
              type="button"
              onClick={() => openAction("start_processing")}
              className="rounded-2xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-blue-500 hover:text-white"
            >
              Start processing
            </button>
          )}

          {canShowCapture && (
            <>
              <button
                type="button"
                onClick={() => openAction("authorize")}
                className="rounded-2xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-blue-500 hover:text-white"
              >
                Authorize
              </button>

              <button
                type="button"
                onClick={() => openAction("capture")}
                className="rounded-2xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-blue-500 hover:text-white"
              >
                Capture
              </button>

              <button
                type="button"
                onClick={() => openAction("charge")}
                className="rounded-2xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-blue-500 hover:text-white"
              >
                Charge
              </button>
            </>
          )}

          {canShowFail && (
            <button
              type="button"
              onClick={() => openAction("fail")}
              className="rounded-2xl border border-amber-500/30 bg-amber-500/10 px-4 py-2 text-sm font-medium text-amber-300 transition hover:bg-amber-500/20"
            >
              Mark as failed
            </button>
          )}

          {canShowCancel && (
            <button
              type="button"
              onClick={() => openAction("cancel")}
              className="rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm font-medium text-red-300 transition hover:bg-red-500/20"
            >
              Cancel payment
            </button>
          )}

          {canShowRefund && (
            <button
              type="button"
              onClick={() => openAction("refund")}
              className="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-sm font-medium text-emerald-300 transition hover:bg-emerald-500/20"
            >
              Create refund
            </button>
          )}
        </div>
      </div>

      <ConfirmActionDialog
        isOpen={dialogOpen}
        title="Confirm payment action"
        description="This operation will be sent to the payment workflow. Please confirm to continue."
        confirmLabel="Confirm"
        cancelLabel="Back"
        isPending={isPending}
        tone={selectedAction === "cancel" ? "danger" : "default"}
        onConfirm={handleConfirm}
        onCancel={closeDialog}
      />
    </>
  );
}