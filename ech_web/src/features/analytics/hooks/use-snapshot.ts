import { useQuery } from "@tanstack/react-query";
import { retrieveSnapshot } from "@/features/analytics/api/retrieve-snapshot";
import { analyticsQueryKeys } from "@/features/analytics/utils/analytics-query-keys";

export function useSnapshot(id: string) {
  return useQuery({
    queryKey: analyticsQueryKeys.snapshotDetail(id),
    queryFn: () => retrieveSnapshot(id),
    enabled: !!id,
  });
}