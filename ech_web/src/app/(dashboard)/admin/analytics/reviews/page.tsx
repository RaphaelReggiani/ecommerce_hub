"use client";

import { ErrorState } from "@/components/feedback/error-state";
import { LoadingState } from "@/components/feedback/loading-state";
import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";
import { ReviewsChart } from "@/features/analytics/components/reviews-chart";
import { useReviewOverview } from "@/features/analytics/hooks/use-review-overview";
import { getDefaultAnalyticsFilters } from "@/features/analytics/utils/analytics-mappers";

export default function AnalyticsReviewsPage() {
  const filters = getDefaultAnalyticsFilters();
  const { data, isLoading, isError, refetch } = useReviewOverview(filters);

  if (isLoading) {
    return (
      <PageContainer>
        <LoadingState title="Loading review analytics..." />
      </PageContainer>
    );
  }

  if (isError || !data) {
    return (
      <PageContainer>
        <ErrorState
          title="Unable to load review analytics."
          description="Review analytics data is currently unavailable."
          onRetry={() => refetch()}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageTitle
        eyebrow="Analytics"
        title="Reviews overview"
        description="Monitor review moderation, verified purchases, and rating quality."
      />

      <ReviewsChart data={data} />
    </PageContainer>
  );
}