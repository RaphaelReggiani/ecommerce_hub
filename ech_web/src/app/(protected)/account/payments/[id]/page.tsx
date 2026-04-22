"use client";

import Link from "next/link";
import { useParams } from "next/navigation";

import { ErrorState } from "@/components/feedback/error-state";
import { LoadingState } from "@/components/feedback/loading-state";
import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";
import { PaymentDetailCard } from "@/features/payments/components/payment-detail-card";
import { usePayment } from "@/features/payments/hooks/use-payment";
import { routes } from "@/config/routes";
import { formatCurrency } from "@/lib/utils/format-currency";
import { formatDateTime } from "@/lib/utils/format-date";

export default function AccountPaymentDetailPage() {
  const params = useParams<{ id: string }>();
  const paymentId = params?.id;
  const { data, isLoading, isError, refetch } = usePayment(paymentId);

  if (isLoading) {
    return (
      <PageContainer>
        <LoadingState
          title="Loading payment..."
          description="Please wait while we load the payment details."
        />
      </PageContainer>
    );
  }

  if (isError || !data) {
    return (
      <PageContainer>
        <ErrorState
          title="Unable to load payment."
          description="We could not retrieve this payment record right now."
          onRetry={() => refetch()}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageTitle
        eyebrow="Payment detail"
        title={data.payment_reference}
        description="Review the complete payment record, lifecycle, and related financial information."
        actions={
          <Link
            href={routes.protected.payments}
            className="inline-flex items-center rounded-2xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-blue-500 hover:text-white"
          >
            Back to payments
          </Link>
        }
      />

      <PaymentDetailCard payment={data} />

      {!!data.transactions.length && (
        <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
          <div className="mb-6">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
              Transactions
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-white">
              Transaction history
            </h2>
          </div>

          <div className="space-y-4">
            {data.transactions.map((transaction) => (
              <div
                key={transaction.id}
                className="rounded-2xl border border-slate-800 bg-slate-950 p-4"
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p className="text-sm font-medium capitalize text-white">
                      {transaction.transaction_type.replaceAll("_", " ")}
                    </p>
                    <p className="mt-1 text-xs text-slate-400">
                      {formatDateTime(transaction.created_at)}
                    </p>
                  </div>

                  <div className="text-left sm:text-right">
                    <p className="text-sm font-medium text-blue-400">
                      {formatCurrency(Number(transaction.amount))}
                    </p>
                    <p className="mt-1 text-xs capitalize text-slate-400">
                      {transaction.status.replaceAll("_", " ")}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {!!data.refunds.length && (
        <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
          <div className="mb-6">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
              Refunds
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-white">
              Refund history
            </h2>
          </div>

          <div className="space-y-4">
            {data.refunds.map((refund) => (
              <div
                key={refund.id}
                className="rounded-2xl border border-slate-800 bg-slate-950 p-4"
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p className="text-sm font-medium text-white">{refund.reason}</p>
                    <p className="mt-1 text-xs text-slate-400">
                      {formatDateTime(refund.created_at)}
                    </p>
                  </div>

                  <div className="text-left sm:text-right">
                    <p className="text-sm font-medium text-blue-400">
                      {formatCurrency(Number(refund.amount))}
                    </p>
                    <p className="mt-1 text-xs capitalize text-slate-400">
                      {refund.status.replaceAll("_", " ")}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </PageContainer>
  );
}