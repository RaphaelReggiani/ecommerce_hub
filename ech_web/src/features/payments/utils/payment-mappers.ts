import type {
  PaymentDetail,
  PaymentListItem,
  PaymentRefund,
  PaymentStatus,
} from "@/features/payments/types/payment";

export function getPaymentDisplayAmount(payment: PaymentListItem | PaymentDetail): string {
  return payment.amount;
}

export function getPaymentRemainingRefundableAmount(
  payment: Pick<PaymentListItem, "amount" | "refunded_amount">,
): number {
  const amount = Number(payment.amount);
  const refunded = Number(payment.refunded_amount);

  if (Number.isNaN(amount) || Number.isNaN(refunded)) {
    return 0;
  }

  return Math.max(amount - refunded, 0);
}

export function isPaymentFullyRefunded(
  payment: Pick<PaymentListItem, "amount" | "refunded_amount">,
): boolean {
  return getPaymentRemainingRefundableAmount(payment) === 0 && Number(payment.refunded_amount) > 0;
}

export function isPaymentPartiallyRefunded(
  payment: Pick<PaymentListItem, "amount" | "refunded_amount">,
): boolean {
  const amount = Number(payment.amount);
  const refunded = Number(payment.refunded_amount);

  if (Number.isNaN(amount) || Number.isNaN(refunded)) {
    return false;
  }

  return refunded > 0 && refunded < amount;
}

export function canProcessPayment(status: PaymentStatus): boolean {
  return status === "pending" || status === "processing" || status === "authorized";
}

export function canCancelPayment(status: PaymentStatus): boolean {
  return status === "pending" || status === "processing" || status === "authorized";
}

export function canRefundPayment(
  payment: Pick<PaymentListItem, "status" | "amount" | "refunded_amount">,
): boolean {
  if (
    payment.status !== "captured" &&
    payment.status !== "partially_refunded"
  ) {
    return false;
  }

  return getPaymentRemainingRefundableAmount(payment) > 0;
}

export function getLatestRefund(refunds: PaymentRefund[]): PaymentRefund | null {
  if (!refunds.length) {
    return null;
  }

  return refunds[0] ?? null;
}