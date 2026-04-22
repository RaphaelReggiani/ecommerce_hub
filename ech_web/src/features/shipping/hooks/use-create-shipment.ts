"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createShipment } from "@/features/shipping/api/create-shipment";
import type { CreateShipmentInput } from "@/features/shipping/types/shipment";
import { shipmentQueryKeys } from "@/features/shipping/utils/shipment-query-keys";

export function useCreateShipment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateShipmentInput) => createShipment(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: shipmentQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: shipmentQueryKeys.managementLists() });
    },
  });
}