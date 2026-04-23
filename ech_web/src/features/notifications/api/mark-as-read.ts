import { apiClient } from "@/lib/api/client";
import type { NotificationDetail } from "../types/notification";

export async function markNotificationAsRead(
  id: string,
): Promise<NotificationDetail> {
  return apiClient.post<NotificationDetail>(
    `/notifications/${id}/read/`,
    undefined,
    { auth: true },
  );
}