"use client";

import { ErrorState } from "@/components/feedback/error-state";
import { LoadingState } from "@/components/feedback/loading-state";
import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";
import { SalesChart } from "@/features/analytics/components/sales-chart";
import { useSalesOverview } from "@/features/analytics/hooks/use-sales-overview";
import { getDefaultAnalyticsFilters } from "@/features/analytics/utils/analytics-mappers";

export default function AnalyticsSalesPage() {
  const filters = getDefaultAnalyticsFilters();
  const { data, isLoading, isError, refetch } = useSalesOverview(filters);

  if (isLoading) {
    return (
      <PageContainer>
        <LoadingState title="Loading sales analytics..." />
      </PageContainer>
    );
  }

  if (isError || !data) {
    return (
      <PageContainer>
        <ErrorState
          title="Unable to load sales analytics."
          description="Sales analytics data is currently unavailable."
          onRetry={() => refetch()}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageTitle
        eyebrow="Analytics"
        title="Sales overview"
        description="Monitor sales, revenue, refunds, and average order value."
      />

      <SalesChart data={data} />
    </PageContainer>
  );
}