"use client";

import { ErrorState } from "@/components/feedback/error-state";
import { LoadingState } from "@/components/feedback/loading-state";
import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";
import { PaymentsChart } from "@/features/analytics/components/payments-chart";
import { usePaymentOverview } from "@/features/analytics/hooks/use-payment-overview";
import { getDefaultAnalyticsFilters } from "@/features/analytics/utils/analytics-mappers";

export default function AnalyticsPaymentsPage() {
  const filters = getDefaultAnalyticsFilters();
  const { data, isLoading, isError, refetch } = usePaymentOverview(filters);

  if (isLoading) {
    return (
      <PageContainer>
        <LoadingState title="Loading payment analytics..." />
      </PageContainer>
    );
  }

  if (isError || !data) {
    return (
      <PageContainer>
        <ErrorState
          title="Unable to load payment analytics."
          description="Payment analytics data is currently unavailable."
          onRetry={() => refetch()}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageTitle
        eyebrow="Analytics"
        title="Payments overview"
        description="Monitor captured, failed, and refunded payments."
      />

      <PaymentsChart data={data} />
    </PageContainer>
  );
}