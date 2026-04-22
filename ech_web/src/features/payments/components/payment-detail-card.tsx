import Link from "next/link";

import { PaymentStatusBadge } from "@/features/payments/components/payment-status-badge";
import type { PaymentDetail } from "@/features/payments/types/payment";
import { routes } from "@/config/routes";
import { formatCurrency } from "@/lib/utils/format-currency";
import { formatDateTime } from "@/lib/utils/format-date";

type PaymentDetailCardProps = {
  payment: PaymentDetail;
};

export function PaymentDetailCard({ payment }: PaymentDetailCardProps) {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
      <div className="mb-6 flex flex-col gap-4 border-b border-slate-800 pb-6 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Payment
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-white">
            {payment.payment_reference}
          </h2>
          <p className="mt-2 text-sm text-slate-400">
            Order:{" "}
            <Link
              href={routes.protected.orderDetail(payment.order)}
              className="text-blue-400 transition hover:text-blue-300"
            >
              {payment.order}
            </Link>
          </p>
        </div>

        <PaymentStatusBadge status={payment.status} />
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Method
          </p>
          <p className="mt-2 text-sm capitalize text-white">
            {payment.method.replaceAll("_", " ")}
          </p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Amount
          </p>
          <p className="mt-2 text-sm font-medium text-blue-400">
            {formatCurrency(Number(payment.amount))}
          </p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Refunded amount
          </p>
          <p className="mt-2 text-sm text-slate-200">
            {formatCurrency(Number(payment.refunded_amount))}
          </p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Customer
          </p>
          <p className="mt-2 text-sm text-white">{payment.customer_name}</p>
          <p className="mt-1 text-xs text-slate-400">{payment.customer_email}</p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Gateway
          </p>
          <p className="mt-2 text-sm text-white">{payment.gateway_name || "-"}</p>
          <p className="mt-1 text-xs text-slate-400">
            Payment ID: {payment.gateway_payment_id || "-"}
          </p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Created
          </p>
          <p className="mt-2 text-sm text-white">
            {formatDateTime(payment.created_at)}
          </p>
          <p className="mt-1 text-xs text-slate-400">
            Updated: {formatDateTime(payment.updated_at)}
          </p>
        </div>
      </div>

      {(payment.failure_code || payment.failure_message) && (
        <div className="mt-6 rounded-2xl border border-red-500/20 bg-red-500/10 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-red-300">
            Failure information
          </p>
          <p className="mt-2 text-sm text-red-100">
            {payment.failure_message || "Payment failure reported."}
          </p>
          {payment.failure_code ? (
            <p className="mt-1 text-xs text-red-200/80">
              Code: {payment.failure_code}
            </p>
          ) : null}
        </div>
      )}

      {payment.lifecycle ? (
        <div className="mt-6">
          <div className="mb-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
              Lifecycle
            </p>
            <h3 className="mt-2 text-xl font-semibold text-white">
              Payment timeline
            </h3>
          </div>

          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {[
              ["Processing started", payment.lifecycle.processing_started_at],
              ["Authorized", payment.lifecycle.authorized_at],
              ["Captured", payment.lifecycle.captured_at],
              ["Failed", payment.lifecycle.failed_at],
              ["Cancelled", payment.lifecycle.cancelled_at],
              ["Refunded", payment.lifecycle.refunded_at],
            ].map(([label, value]) => (
              <div
                key={label}
                className="rounded-2xl border border-slate-800 bg-slate-950 p-4"
              >
                <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
                  {label}
                </p>
                <p className="mt-2 text-sm text-slate-200">
                  {typeof value === "string" && value
                    ? formatDateTime(value)
                    : "Not reached"}
                </p>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}