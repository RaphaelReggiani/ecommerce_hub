"use client";

import { ErrorState } from "@/components/feedback/error-state";
import { LoadingState } from "@/components/feedback/loading-state";
import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";
import { AlertsList } from "@/features/admin-dashboard/components/alerts-list";
import { BulkActionsPanel } from "@/features/admin-dashboard/components/bulk-actions-panel";
import { OperationalMetricsGrid } from "@/features/admin-dashboard/components/operational-metrics-grid";
import { RecentActivityTable } from "@/features/admin-dashboard/components/recent-activity-table";
import { SummaryCards } from "@/features/admin-dashboard/components/summary-cards";
import { useAdminAlerts } from "@/features/admin-dashboard/hooks/use-admin-alerts";
import { useAdminOperationalMetrics } from "@/features/admin-dashboard/hooks/use-admin-operational-metrics";
import { useAdminRecentActivity } from "@/features/admin-dashboard/hooks/use-admin-recent-activity";
import { useAdminSummary } from "@/features/admin-dashboard/hooks/use-admin-summary";

export default function AdminDashboardPage() {
  const summaryQuery = useAdminSummary();
  const metricsQuery = useAdminOperationalMetrics();
  const alertsQuery = useAdminAlerts();
  const activityQuery = useAdminRecentActivity(20);

  const isLoading =
    summaryQuery.isLoading ||
    metricsQuery.isLoading ||
    alertsQuery.isLoading ||
    activityQuery.isLoading;

  const isError =
    summaryQuery.isError ||
    metricsQuery.isError ||
    alertsQuery.isError ||
    activityQuery.isError;

  if (isLoading) {
    return (
      <PageContainer>
        <LoadingState
          title="Loading admin dashboard..."
          description="Please wait while we load operational data."
        />
      </PageContainer>
    );
  }

  if (
    isError ||
    !summaryQuery.data ||
    !metricsQuery.data ||
    !alertsQuery.data ||
    !activityQuery.data
  ) {
    return (
      <PageContainer>
        <ErrorState
          title="Unable to load admin dashboard."
          description="Admin dashboard data is currently unavailable."
          onRetry={() => {
            summaryQuery.refetch();
            metricsQuery.refetch();
            alertsQuery.refetch();
            activityQuery.refetch();
          }}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageTitle
        eyebrow="Admin"
        title="Admin dashboard"
        description="Monitor platform operations, alerts, recent activity, and controlled bulk actions."
      />

      <div className="space-y-8">
        <SummaryCards summary={summaryQuery.data} />

        <OperationalMetricsGrid metrics={metricsQuery.data} />

        <div className="grid gap-8 xl:grid-cols-[1fr_1.2fr]">
          <AlertsList alerts={alertsQuery.data} />
          <RecentActivityTable activity={activityQuery.data} />
        </div>

        <BulkActionsPanel />
      </div>
    </PageContainer>
  );
}