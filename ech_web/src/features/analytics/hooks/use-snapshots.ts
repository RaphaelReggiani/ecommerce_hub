import { useQuery } from "@tanstack/react-query";
import { listSnapshots } from "@/features/analytics/api/list-snapshots";
import { analyticsQueryKeys } from "@/features/analytics/utils/analytics-query-keys";

export function useSnapshots(filters = {}) {
  return useQuery({
    queryKey: analyticsQueryKeys.snapshots(filters),
    queryFn: () => listSnapshots(filters),
  });
}