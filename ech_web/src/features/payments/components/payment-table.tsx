"use client";

import Link from "next/link";

import { EmptyState } from "@/components/feedback/empty-state";
import { PaymentStatusBadge } from "@/features/payments/components/payment-status-badge";
import type { PaymentListItem } from "@/features/payments/types/payment";
import { routes } from "@/config/routes";
import { formatCurrency } from "@/lib/utils/format-currency";
import { formatDateTime } from "@/lib/utils/format-date";

type PaymentTableProps = {
  payments: PaymentListItem[];
};

export function PaymentTable({ payments }: PaymentTableProps) {
  if (!payments.length) {
    return (
      <EmptyState
        title="No payments found."
        description="There are no payment records available for your account yet."
      />
    );
  }

  return (
    <div className="overflow-hidden rounded-3xl border border-slate-800 bg-slate-900/70 shadow-xl">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-800">
          <thead className="bg-slate-950/70">
            <tr>
              <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                Reference
              </th>
              <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                Method
              </th>
              <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                Status
              </th>
              <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                Amount
              </th>
              <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                Refunded
              </th>
              <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                Gateway
              </th>
              <th className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] text-slate-500">
                Created
              </th>
              <th className="px-6 py-4 text-right text-xs uppercase tracking-[0.2em] text-slate-500">
                Action
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-800">
            {payments.map((payment) => (
              <tr key={payment.id} className="hover:bg-slate-950/40">
                <td className="px-6 py-4 text-sm text-white">
                  <div className="font-medium">{payment.payment_reference}</div>
                  <div className="text-slate-500">{payment.currency}</div>
                </td>

                <td className="px-6 py-4 text-sm capitalize text-slate-300">
                  {payment.method.replaceAll("_", " ")}
                </td>

                <td className="px-6 py-4">
                  <PaymentStatusBadge status={payment.status} />
                </td>

                <td className="px-6 py-4 text-sm font-medium text-blue-400">
                  {formatCurrency(Number(payment.amount))}
                </td>

                <td className="px-6 py-4 text-sm text-slate-300">
                  {formatCurrency(Number(payment.refunded_amount))}
                </td>

                <td className="px-6 py-4 text-sm text-slate-400">
                  {payment.gateway_name || "-"}
                </td>

                <td className="px-6 py-4 text-sm text-slate-400">
                  {formatDateTime(payment.created_at)}
                </td>

                <td className="px-6 py-4 text-right">
                  <Link
                    href={routes.protected.paymentDetail(payment.id)}
                    className="inline-flex rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-blue-500 hover:text-white"
                  >
                    View details
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}