"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { cancelShipment } from "@/features/shipping/api/cancel-shipment";
import type { CancelShipmentInput } from "@/features/shipping/types/shipment";
import { shipmentQueryKeys } from "@/features/shipping/utils/shipment-query-keys";

export function useCancelShipment(shipmentId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CancelShipmentInput = {}) =>
      cancelShipment(shipmentId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: shipmentQueryKeys.detail(shipmentId) });
      queryClient.invalidateQueries({ queryKey: shipmentQueryKeys.managementDetail(shipmentId) });
      queryClient.invalidateQueries({ queryKey: shipmentQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: shipmentQueryKeys.managementLists() });
    },
  });
}