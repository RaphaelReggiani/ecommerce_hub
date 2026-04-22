"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { processShipment } from "@/features/shipping/api/process-shipment";
import type { ProcessShipmentInput } from "@/features/shipping/types/shipment";
import { shipmentQueryKeys } from "@/features/shipping/utils/shipment-query-keys";

export function useProcessShipment(shipmentId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ProcessShipmentInput) =>
      processShipment(shipmentId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: shipmentQueryKeys.detail(shipmentId) });
      queryClient.invalidateQueries({ queryKey: shipmentQueryKeys.managementDetail(shipmentId) });
      queryClient.invalidateQueries({ queryKey: shipmentQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: shipmentQueryKeys.managementLists() });
    },
  });
}