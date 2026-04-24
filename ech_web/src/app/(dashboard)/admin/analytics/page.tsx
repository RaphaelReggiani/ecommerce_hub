"use client";

import { useState } from "react";

import { ErrorState } from "@/components/feedback/error-state";
import { LoadingState } from "@/components/feedback/loading-state";
import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";
import { AnalyticsFilters } from "@/features/analytics/components/analytics-filters";
import { AnalyticsSummaryCards } from "@/features/analytics/components/analytics-summary-cards";
import { RevenueChart } from "@/features/analytics/components/revenue-chart";
import { useDashboardSummary } from "@/features/analytics/hooks/use-dashboard-summary";
import type { AnalyticsPeriodFilters } from "@/features/analytics/types/analytics";
import { getDefaultAnalyticsFilters } from "@/features/analytics/utils/analytics-mappers";

export default function AnalyticsDashboardPage() {
  const [filters, setFilters] = useState<AnalyticsPeriodFilters>(
    getDefaultAnalyticsFilters(),
  );

  const { data, isLoading, isError, refetch } = useDashboardSummary(filters);

  if (isLoading) {
    return (
      <PageContainer>
        <LoadingState
          title="Loading analytics..."
          description="Please wait while we load your dashboard metrics."
        />
      </PageContainer>
    );
  }

  if (isError || !data) {
    return (
      <PageContainer>
        <ErrorState
          title="Unable to load analytics."
          description="Analytics data is currently unavailable."
          onRetry={() => refetch()}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageTitle
        eyebrow="Admin Analytics"
        title="Analytics dashboard"
        description="Monitor platform performance through period-based business metrics."
      />

      <div className="space-y-8">
        <AnalyticsFilters initialFilters={filters} onApply={setFilters} />

        <AnalyticsSummaryCards data={data} />

        <div className="grid gap-6 xl:grid-cols-2">
          <RevenueChart data={data} />

          <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
            <h2 className="text-xl font-semibold text-white">
              Snapshot source
            </h2>

            <div className="mt-6 space-y-4 text-sm text-slate-300">
              <p>
                <span className="text-slate-500">Source:</span> {data.source}
              </p>
              <p>
                <span className="text-slate-500">Period:</span>{" "}
                {data.period_type ?? "-"}
              </p>
              <p>
                <span className="text-slate-500">Snapshot:</span>{" "}
                {data.snapshot_id ?? "Computed"}
              </p>
              <p>
                <span className="text-slate-500">Period start:</span>{" "}
                {data.period_start ?? "-"}
              </p>
              <p>
                <span className="text-slate-500">Period end:</span>{" "}
                {data.period_end}
              </p>
            </div>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}