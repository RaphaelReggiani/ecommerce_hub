"use client";

import { useQuery } from "@tanstack/react-query";
import { retrieveNotification } from "../api/retrieve-notification";
import { notificationQueryKeys } from "../utils/notification-query-keys";

export function useNotification(id: string) {
  return useQuery({
    queryKey: notificationQueryKeys.detail(id),
    queryFn: () => retrieveNotification(id),
    enabled: Boolean(id),
  });
}