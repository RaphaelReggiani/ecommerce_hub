"use client";

import { ErrorState } from "@/components/feedback/error-state";
import { LoadingState } from "@/components/feedback/loading-state";
import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";
import { CustomersChart } from "@/features/analytics/components/customers-chart";
import { useCustomerSummary } from "@/features/analytics/hooks/use-customer-summary";
import { getDefaultAnalyticsFilters } from "@/features/analytics/utils/analytics-mappers";

export default function AnalyticsCustomersPage() {
  const filters = getDefaultAnalyticsFilters();
  const { data, isLoading, isError, refetch } = useCustomerSummary(filters);

  if (isLoading) {
    return (
      <PageContainer>
        <LoadingState title="Loading customer analytics..." />
      </PageContainer>
    );
  }

  if (isError || !data) {
    return (
      <PageContainer>
        <ErrorState
          title="Unable to load customer analytics."
          description="Customer analytics data is currently unavailable."
          onRetry={() => refetch()}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageTitle
        eyebrow="Analytics"
        title="Customer summary"
        description="Monitor active customers, new customers, growth, and repeat rate."
      />

      <CustomersChart data={data} />
    </PageContainer>
  );
}