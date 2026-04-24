import { KpiCard } from "@/features/analytics/components/kpi-card";
import { MetricsGrid } from "@/features/analytics/components/metrics-grid";
import type { DashboardSummary } from "@/features/analytics/types/dashboard";
import {
  formatAnalyticsCurrency,
  formatAnalyticsNumber,
} from "@/features/analytics/utils/analytics-formatters";

type AnalyticsSummaryCardsProps = {
  data: DashboardSummary;
};

export function AnalyticsSummaryCards({ data }: AnalyticsSummaryCardsProps) {
  return (
    <MetricsGrid>
      <KpiCard
        title="Total Revenue"
        value={formatAnalyticsCurrency(data.revenue.total_revenue)}
        description="Gross revenue generated in the selected period."
      />

      <KpiCard
        title="Net Revenue"
        value={formatAnalyticsCurrency(data.revenue.net_revenue)}
        description="Revenue after refunds."
      />

      <KpiCard
        title="Orders"
        value={formatAnalyticsNumber(data.orders.total_orders)}
        description="Total orders created in the selected period."
      />

      <KpiCard
        title="Active Customers"
        value={formatAnalyticsNumber(data.customers.active_customers)}
        description="Customers with activity during the period."
      />

      <KpiCard
        title="Products Sold"
        value={formatAnalyticsNumber(data.products.products_sold)}
        description="Total sold product units."
      />

      <KpiCard
        title="Captured Payments"
        value={formatAnalyticsNumber(data.payments.payments_captured)}
        description="Successful captured payments."
      />

      <KpiCard
        title="Delivered Shipments"
        value={formatAnalyticsNumber(data.shipping.shipments_delivered)}
        description="Shipments delivered successfully."
      />

      <KpiCard
        title="Average Rating"
        value={data.reviews.average_rating}
        description="Average review rating for the period."
      />
    </MetricsGrid>
  );
}