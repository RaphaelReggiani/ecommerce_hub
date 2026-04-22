"use client";

import { ErrorState } from "@/components/feedback/error-state";
import { LoadingState } from "@/components/feedback/loading-state";
import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";
import { PaymentTable } from "@/features/payments/components/payment-table";
import { usePayments } from "@/features/payments/hooks/use-payments";

export default function AccountPaymentsPage() {
  const { data, isLoading, isError, refetch } = usePayments();

  if (isLoading) {
    return (
      <PageContainer>
        <LoadingState
          title="Loading payments..."
          description="Please wait while we load your payment history."
        />
      </PageContainer>
    );
  }

  if (isError || !data) {
    return (
      <PageContainer>
        <ErrorState
          title="Unable to load payments."
          description="We could not retrieve your payment history right now."
          onRetry={() => refetch()}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageTitle
        eyebrow="Payments"
        title="Your payments"
        description="Review your payment history, statuses, and payment records linked to your orders."
      />

      <PaymentTable payments={data.results} />
    </PageContainer>
  );
}