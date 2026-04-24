import { apiClient } from "@/lib/api/client";
import type {
  BulkNotificationRetryInput,
  BulkNotificationRetryResponse,
} from "@/features/admin-dashboard/types/admin-dashboard";

export async function retryBulkNotifications(
  payload: BulkNotificationRetryInput,
): Promise<BulkNotificationRetryResponse> {
  return apiClient.post<BulkNotificationRetryResponse>(
    "/admin-dashboard/notifications/retry/",
    payload,
    { auth: true },
  );
}