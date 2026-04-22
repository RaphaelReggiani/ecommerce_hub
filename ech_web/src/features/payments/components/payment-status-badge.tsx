import { StatusBadge } from "@/components/shared/status-badge";
import {
  getPaymentStatusLabel,
  getPaymentStatusTone,
} from "@/lib/constants/statuses";

import type { PaymentStatus } from "@/features/payments/types/payment";

type PaymentStatusBadgeProps = {
  status: PaymentStatus;
};

export function PaymentStatusBadge({ status }: PaymentStatusBadgeProps) {
  return (
    <StatusBadge tone={getPaymentStatusTone(status)}>
      {getPaymentStatusLabel(status)}
    </StatusBadge>
  );
}