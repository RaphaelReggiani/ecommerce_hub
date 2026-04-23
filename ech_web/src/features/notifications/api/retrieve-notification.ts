import { apiClient } from "@/lib/api/client";
import type { NotificationDetail } from "../types/notification";

export async function retrieveNotification(
  id: string,
): Promise<NotificationDetail> {
  return apiClient.get<NotificationDetail>(
    `/notifications/${id}/`,
    { auth: true },
  );
}