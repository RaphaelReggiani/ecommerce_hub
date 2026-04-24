import { KpiCard } from "@/features/analytics/components/kpi-card";
import { MetricsGrid } from "@/features/analytics/components/metrics-grid";
import type { AdminDashboardOperationalMetrics } from "@/features/admin-dashboard/types/admin-dashboard";
import { formatAnalyticsNumber } from "@/features/analytics/utils/analytics-formatters";

type OperationalMetricsGridProps = {
  metrics: AdminDashboardOperationalMetrics;
};

export function OperationalMetricsGrid({ metrics }: OperationalMetricsGridProps) {
  return (
    <MetricsGrid>
      <KpiCard title="Pending Orders" value={formatAnalyticsNumber(metrics.orders.pending_orders)} />
      <KpiCard title="Failed Payments" value={formatAnalyticsNumber(metrics.payments.failed_payments)} />
      <KpiCard title="Failed Shipments" value={formatAnalyticsNumber(metrics.shipping.failed_shipments)} />
      <KpiCard title="Pending Moderation" value={formatAnalyticsNumber(metrics.reviews.pending_moderation)} />
      <KpiCard title="Failed Notifications" value={formatAnalyticsNumber(metrics.notifications.failed_notifications)} />
      <KpiCard title="Low Stock Products" value={formatAnalyticsNumber(metrics.products.low_stock_products)} />
      <KpiCard title="Out of Stock" value={formatAnalyticsNumber(metrics.products.out_of_stock_products)} />
      <KpiCard title="Products Without Images" value={formatAnalyticsNumber(metrics.products.products_without_images)} />
    </MetricsGrid>
  );
}