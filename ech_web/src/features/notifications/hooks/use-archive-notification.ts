"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { archiveNotification } from "@/features/notifications/api/archive-notification";
import { notificationQueryKeys } from "@/features/notifications/utils/notification-query-keys";

export function useArchiveNotification() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => archiveNotification(id),
    onSuccess: (notification) => {
      queryClient.invalidateQueries({
        queryKey: notificationQueryKeys.all,
      });

      queryClient.setQueryData(
        notificationQueryKeys.detail(notification.id),
        notification,
      );
    },
  });
}