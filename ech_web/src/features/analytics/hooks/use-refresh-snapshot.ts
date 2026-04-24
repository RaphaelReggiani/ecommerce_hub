import { useMutation, useQueryClient } from "@tanstack/react-query";
import { refreshSnapshot } from "@/features/analytics/api/refresh-snapshot";
import { analyticsQueryKeys } from "@/features/analytics/utils/analytics-query-keys";

export function useRefreshSnapshot() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id }: { id: string }) => refreshSnapshot(id),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: analyticsQueryKeys.all,
      });
    },
  });
}