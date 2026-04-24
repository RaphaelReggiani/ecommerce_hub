import { KpiCard } from "@/features/analytics/components/kpi-card";
import { MetricsGrid } from "@/features/analytics/components/metrics-grid";
import type { AdminDashboardSummary } from "@/features/admin-dashboard/types/admin-dashboard";
import { formatAnalyticsNumber } from "@/features/analytics/utils/analytics-formatters";

type SummaryCardsProps = {
  summary: AdminDashboardSummary;
};

export function SummaryCards({ summary }: SummaryCardsProps) {
  return (
    <MetricsGrid>
      <KpiCard title="Orders" value={formatAnalyticsNumber(summary.orders.total_orders)} />
      <KpiCard title="Payments" value={formatAnalyticsNumber(summary.payments.total_payments)} />
      <KpiCard title="Shipments" value={formatAnalyticsNumber(summary.shipping.total_shipments)} />
      <KpiCard title="Users" value={formatAnalyticsNumber(summary.users.total_users)} />
      <KpiCard title="Products" value={formatAnalyticsNumber(summary.products.total_products)} />
      <KpiCard title="Reviews" value={formatAnalyticsNumber(summary.reviews.total_reviews)} />
      <KpiCard title="Active Products" value={formatAnalyticsNumber(summary.products.active_products)} />
      <KpiCard title="Pending Reviews" value={formatAnalyticsNumber(summary.reviews.pending_reviews)} />
    </MetricsGrid>
  );
}