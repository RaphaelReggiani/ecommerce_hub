"use client";

import { useQuery } from "@tanstack/react-query";

import {
  listNotifications,
  type ListNotificationsFilters,
} from "@/features/notifications/api/list-notifications";
import { notificationQueryKeys } from "@/features/notifications/utils/notification-query-keys";

type UseNotificationsOptions = {
  enabled?: boolean;
};

export function useNotifications(
  filters: ListNotificationsFilters = {},
  options: UseNotificationsOptions = {},
) {
  return useQuery({
    queryKey: notificationQueryKeys.list(filters),
    queryFn: () => listNotifications(filters),
    enabled: options.enabled ?? true,
  });
}