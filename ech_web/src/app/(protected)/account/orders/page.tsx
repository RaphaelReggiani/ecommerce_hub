"use client";

import { ErrorState } from "@/components/feedback/error-state";
import { LoadingState } from "@/components/feedback/loading-state";
import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";
import { OrderTable } from "@/features/orders/components/order-table";
import { useOrders } from "@/features/orders/hooks/use-orders";

export default function AccountOrdersPage() {
  const { data, isLoading, isError, refetch } = useOrders();

  if (isLoading) {
    return (
      <PageContainer>
        <LoadingState
          title="Loading orders..."
          description="Please wait while we load your order history."
        />
      </PageContainer>
    );
  }

  if (isError || !data) {
    return (
      <PageContainer>
        <ErrorState
          title="Unable to load orders."
          description="We could not retrieve your order history right now."
          onRetry={() => refetch()}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageTitle
        eyebrow="Orders"
        title="Your orders"
        description="Review your purchases, payment status, shipping progress, and order details."
      />

      <OrderTable orders={data.results} />
    </PageContainer>
  );
}