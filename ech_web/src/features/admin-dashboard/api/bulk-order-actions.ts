import { apiClient } from "@/lib/api/client";
import type {
  BulkOrderActionInput,
  BulkOrderActionResponse,
} from "@/features/admin-dashboard/types/admin-dashboard";

export async function executeBulkOrderAction(
  payload: BulkOrderActionInput,
): Promise<BulkOrderActionResponse> {
  return apiClient.post<BulkOrderActionResponse>(
    "/admin-dashboard/orders/bulk-action/",
    payload,
    { auth: true },
  );
}