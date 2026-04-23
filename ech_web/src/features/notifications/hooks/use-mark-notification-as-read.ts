"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { markNotificationAsRead } from "@/features/notifications/api/mark-as-read";
import { notificationQueryKeys } from "@/features/notifications/utils/notification-query-keys";

export function useMarkNotificationAsRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => markNotificationAsRead(id),
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