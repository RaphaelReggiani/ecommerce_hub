import type { ShipmentFiltersInput } from "@/features/shipping/types/shipment";

export const shipmentQueryKeys = {
  all: ["shipping"] as const,

  lists: () => [...shipmentQueryKeys.all, "list"] as const,

  list: (filters: ShipmentFiltersInput = {}) =>
    [...shipmentQueryKeys.lists(), filters] as const,

  details: () => [...shipmentQueryKeys.all, "detail"] as const,

  detail: (shipmentId: string) =>
    [...shipmentQueryKeys.details(), shipmentId] as const,

  managementLists: () => [...shipmentQueryKeys.all, "management", "list"] as const,

  managementDetails: () => [...shipmentQueryKeys.all, "management", "detail"] as const,

  managementDetail: (shipmentId: string) =>
    [...shipmentQueryKeys.managementDetails(), shipmentId] as const,
};