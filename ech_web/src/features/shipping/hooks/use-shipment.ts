"use client";

import { useQuery } from "@tanstack/react-query";

import { retrieveShipment } from "@/features/shipping/api/retrieve-shipment";
import { shipmentQueryKeys } from "@/features/shipping/utils/shipment-query-keys";

export function useShipment(shipmentId?: string) {
  return useQuery({
    queryKey: shipmentQueryKeys.detail(shipmentId ?? ""),
    queryFn: () => {
      if (!shipmentId) {
        throw new Error("Shipment id is required");
      }

      return retrieveShipment(shipmentId);
    },
    enabled: Boolean(shipmentId),
  });
}