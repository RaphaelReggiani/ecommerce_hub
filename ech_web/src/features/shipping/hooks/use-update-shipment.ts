"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { updateShipment } from "@/features/shipping/api/update-shipment";
import type { UpdateShipmentInput } from "@/features/shipping/types/shipment";
import { shipmentQueryKeys } from "@/features/shipping/utils/shipment-query-keys";

export function useUpdateShipment(shipmentId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: UpdateShipmentInput) =>
      updateShipment(shipmentId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: shipmentQueryKeys.detail(shipmentId) });
      queryClient.invalidateQueries({ queryKey: shipmentQueryKeys.managementDetail(shipmentId) });
      queryClient.invalidateQueries({ queryKey: shipmentQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: shipmentQueryKeys.managementLists() });
    },
  });
}