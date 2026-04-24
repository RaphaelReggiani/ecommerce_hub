"use client";

import { ErrorState } from "@/components/feedback/error-state";
import { LoadingState } from "@/components/feedback/loading-state";
import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";
import { OrdersFunnelChart } from "@/features/analytics/components/orders-funnel-chart";
import { useOrderFunnel } from "@/features/analytics/hooks/use-order-funnel";
import { getDefaultAnalyticsFilters } from "@/features/analytics/utils/analytics-mappers";

export default function AnalyticsOrdersPage() {
  const filters = getDefaultAnalyticsFilters();
  const { data, isLoading, isError, refetch } = useOrderFunnel(filters);

  if (isLoading) {
    return (
      <PageContainer>
        <LoadingState title="Loading order analytics..." />
      </PageContainer>
    );
  }

  if (isError || !data) {
    return (
      <PageContainer>
        <ErrorState
          title="Unable to load order analytics."
          description="Order funnel analytics data is currently unavailable."
          onRetry={() => refetch()}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageTitle
        eyebrow="Analytics"
        title="Order funnel"
        description="Track order lifecycle distribution and conversion rates."
      />

      <OrdersFunnelChart data={data} />
    </PageContainer>
  );
}