import { apiClient } from "@/lib/api/client";
import type { AnalyticsSnapshotDetail } from "@/features/analytics/types/snapshot";

export type RefreshSnapshotPayload = {
  metadata?: Record<string, unknown>;
};

export async function refreshSnapshot(
  id: string,
  payload: RefreshSnapshotPayload = {},
): Promise<AnalyticsSnapshotDetail> {
  return apiClient.post<AnalyticsSnapshotDetail>(
    `/analytics/snapshots/${id}/refresh/`,
    payload,
    { auth: true },
  );
}