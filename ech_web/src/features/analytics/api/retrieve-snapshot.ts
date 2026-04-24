import { apiClient } from "@/lib/api/client";
import type { AnalyticsSnapshotDetail } from "@/features/analytics/types/snapshot";

export async function retrieveSnapshot(
  id: string,
): Promise<AnalyticsSnapshotDetail> {
  return apiClient.get<AnalyticsSnapshotDetail>(
    `/analytics/snapshots/${id}/`,
    { auth: true },
  );
}