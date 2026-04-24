"use client";

import { ErrorState } from "@/components/feedback/error-state";
import { LoadingState } from "@/components/feedback/loading-state";
import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";
import { ShippingChart } from "@/features/analytics/components/shipping-chart";
import { useShippingOverview } from "@/features/analytics/hooks/use-shipping-overview";
import { getDefaultAnalyticsFilters } from "@/features/analytics/utils/analytics-mappers";

export default function AnalyticsShippingPage() {
  const filters = getDefaultAnalyticsFilters();
  const { data, isLoading, isError, refetch } = useShippingOverview(filters);

  if (isLoading) {
    return (
      <PageContainer>
        <LoadingState title="Loading shipping analytics..." />
      </PageContainer>
    );
  }

  if (isError || !data) {
    return (
      <PageContainer>
        <ErrorState
          title="Unable to load shipping analytics."
          description="Shipping analytics data is currently unavailable."
          onRetry={() => refetch()}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageTitle
        eyebrow="Analytics"
        title="Shipping overview"
        description="Monitor shipment progress, deliveries, and failed shipments."
      />

      <ShippingChart data={data} />
    </PageContainer>
  );
}