export type PaymentMethod =
  | "credit_card"
  | "debit_card"
  | "pix"
  | "bank_slip"
  | "wallet";

export type PaymentStatus =
  | "pending"
  | "processing"
  | "authorized"
  | "captured"
  | "failed"
  | "cancelled"
  | "partially_refunded"
  | "refunded";

export type PaymentTransactionType =
  | "authorization"
  | "capture"
  | "charge"
  | "refund"
  | "partial_refund"
  | "cancellation"
  | "failure";

export type PaymentTransactionStatus =
  | "pending"
  | "success"
  | "failed"
  | "cancelled";

export type PaymentRefundStatus =
  | "pending"
  | "processed"
  | "failed"
  | "cancelled";

export type PaymentEventType =
  | "created"
  | "processing_started"
  | "authorized"
  | "captured"
  | "failed"
  | "cancelled"
  | "refund_requested"
  | "refund_failed"
  | "refund_cancelled"
  | "partially_refunded"
  | "refunded";

export type PaymentLifecycle = {
  processing_started_at: string | null;
  authorized_at: string | null;
  captured_at: string | null;
  failed_at: string | null;
  cancelled_at: string | null;
  refunded_at: string | null;
  updated_at: string;
};

export type PaymentTransaction = {
  id: string;
  transaction_type: PaymentTransactionType;
  status: PaymentTransactionStatus;
  amount: string;
  currency: string;
  gateway_transaction_id: string;
  gateway_response_code: string;
  gateway_response_message: string;
  metadata: Record<string, unknown> | null;
  performed_by: number | null;
  performed_by_name: string | null;
  performed_by_email: string | null;
  processed_at: string | null;
  created_at: string;
};

export type PaymentRefund = {
  id: string;
  payment: string;
  amount: string;
  reason: string;
  status: PaymentRefundStatus;
  gateway_refund_id: string;
  metadata: Record<string, unknown> | null;
  requested_by: number | null;
  requested_by_name: string | null;
  requested_by_email: string | null;
  processed_by: number | null;
  processed_by_name: string | null;
  processed_by_email: string | null;
  processed_at: string | null;
  created_at: string;
  updated_at: string;
};

export type PaymentEvent = {
  id: string;
  event_type: PaymentEventType | string;
  performed_by: number | null;
  performed_by_name: string | null;
  performed_by_email: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
};

export type PaymentListItem = {
  id: string;
  order: string;
  customer: number;
  customer_name: string;
  customer_email: string;
  payment_reference: string;
  method: PaymentMethod;
  status: PaymentStatus;
  amount: string;
  refunded_amount: string;
  currency: string;
  gateway_name: string;
  created_at: string;
  updated_at: string;
};

export type PaymentDetail = PaymentListItem & {
  gateway_payment_id: string;
  gateway_customer_id: string;
  failure_code: string;
  failure_message: string;
  metadata: Record<string, unknown> | null;
  transactions: PaymentTransaction[];
  refunds: PaymentRefund[];
  lifecycle: PaymentLifecycle | null;
  events: PaymentEvent[];
};

export type PaymentManagementDetail = PaymentDetail & {
  idempotency_key?: string | null;
};

export type PaymentFiltersInput = {
  status?: PaymentStatus;
  method?: PaymentMethod;
  customer_id?: number;
  order_id?: string;
  payment_reference?: string;
  gateway_payment_id?: string;
  min_amount?: number;
  max_amount?: number;
  min_refunded_amount?: number;
  max_refunded_amount?: number;
  created_after?: string;
  created_before?: string;
  is_refunded?: boolean;
  is_partially_refunded?: boolean;
  page?: number;
};

export type CreatePaymentInput = {
  order_id: string;
  method: PaymentMethod;
  payment_reference?: string;
  idempotency_key?: string;
  gateway_name?: string;
  gateway_payment_id?: string;
  gateway_customer_id?: string;
  metadata?: Record<string, unknown>;
};

export type PaymentProcessAction =
  | "start_processing"
  | "authorize"
  | "capture"
  | "charge"
  | "fail";

export type ProcessPaymentInput = {
  action: PaymentProcessAction;
  amount?: string;
  gateway_transaction_id?: string;
  gateway_response_code?: string;
  gateway_response_message?: string;
  failure_code?: string;
  failure_message?: string;
  metadata?: Record<string, unknown>;
};

export type CancelPaymentInput = {
  gateway_transaction_id?: string;
  gateway_response_code?: string;
  gateway_response_message?: string;
  metadata?: Record<string, unknown>;
};

export type CreateRefundInput = {
  amount: string;
  reason: string;
  gateway_refund_id?: string;
  metadata?: Record<string, unknown>;
};

export type RefundManagementAction = "process" | "fail" | "cancel";

export type ManageRefundInput = {
  action: RefundManagementAction;
  gateway_transaction_id?: string;
  metadata?: Record<string, unknown>;
};