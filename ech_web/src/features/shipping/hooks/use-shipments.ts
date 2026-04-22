"use client";

import { useQuery } from "@tanstack/react-query";

import { listShipments } from "@/features/shipping/api/list-shipments";
import type { ShipmentFiltersInput } from "@/features/shipping/types/shipment";
import { shipmentQueryKeys } from "@/features/shipping/utils/shipment-query-keys";

export function useShipments(filters: ShipmentFiltersInput = {}) {
  return useQuery({
    queryKey: shipmentQueryKeys.list(filters),
    queryFn: () => listShipments(filters),
  });
}