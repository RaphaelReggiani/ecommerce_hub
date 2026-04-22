"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { trackShipment } from "@/features/shipping/api/track-shipment";
import type { TrackShipmentInput } from "@/features/shipping/types/shipment";
import { shipmentQueryKeys } from "@/features/shipping/utils/shipment-query-keys";

export function useTrackShipment(shipmentId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: TrackShipmentInput) =>
      trackShipment(shipmentId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: shipmentQueryKeys.detail(shipmentId) });
      queryClient.invalidateQueries({ queryKey: shipmentQueryKeys.managementDetail(shipmentId) });
      queryClient.invalidateQueries({ queryKey: shipmentQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: shipmentQueryKeys.managementLists() });
    },
  });
}