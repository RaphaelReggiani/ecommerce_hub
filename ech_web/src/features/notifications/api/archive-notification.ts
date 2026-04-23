import { apiClient } from "@/lib/api/client";
import type { NotificationDetail } from "../types/notification";

export async function archiveNotification(
  id: string,
): Promise<NotificationDetail> {
  return apiClient.post<NotificationDetail>(
    `/notifications/${id}/archive/`,
    undefined,
    { auth: true },
  );
}