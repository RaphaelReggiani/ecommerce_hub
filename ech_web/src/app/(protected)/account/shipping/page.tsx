"use client";

import { ErrorState } from "@/components/feedback/error-state";
import { LoadingState } from "@/components/feedback/loading-state";
import { PageContainer } from "@/components/layout/page-container";
import { PageTitle } from "@/components/layout/page-title";
import { ShipmentTable } from "@/features/shipping/components/shipment-table";
import { useShipments } from "@/features/shipping/hooks/use-shipments";

export default function AccountShippingPage() {
  const { data, isLoading, isError, refetch } = useShipments();

  if (isLoading) {
    return (
      <PageContainer>
        <LoadingState
          title="Loading shipments..."
          description="Please wait while we load your shipment history."
        />
      </PageContainer>
    );
  }

  if (isError || !data) {
    return (
      <PageContainer>
        <ErrorState
          title="Unable to load shipments."
          description="We could not retrieve your shipment history right now."
          onRetry={() => refetch()}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageTitle
        eyebrow="Shipping"
        title="Your shipments"
        description="Review shipment statuses, carriers, tracking codes, and delivery estimates."
      />

      <ShipmentTable shipments={data.results} />
    </PageContainer>
  );
}