import { apiClient } from "@/lib/api/client";
import type { PaginatedApiResponse } from "@/types/api";
import type { NotificationListItem } from "../types/notification";
import { buildQueryString } from "@/lib/utils/build-query-string";

export type ListNotificationsFilters = {
  status?: string;
  channel?: string;
  priority?: string;
  notification_type?: string;
  source_module?: string;
  created_after?: string;
  created_before?: string;
  scheduled_after?: string;
  scheduled_before?: string;
  page?: number;
};

export async function listNotifications(
  filters: ListNotificationsFilters = {},
): Promise<PaginatedApiResponse<NotificationListItem>> {
  const queryString = buildQueryString(filters);

  return apiClient.get<PaginatedApiResponse<NotificationListItem>>(
    `/notifications/${queryString}`,
    { auth: true },
  );
}