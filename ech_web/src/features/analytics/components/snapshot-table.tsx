import type { AnalyticsSnapshotListItem } from "@/features/analytics/types/snapshot";
import { formatAnalyticsCurrency } from "@/features/analytics/utils/analytics-formatters";
import { formatDateTime } from "@/lib/utils/format-date";

type SnapshotTableProps = {
  snapshots: AnalyticsSnapshotListItem[];
};

export function SnapshotTable({ snapshots }: SnapshotTableProps) {
  if (snapshots.length === 0) {
    return (
      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-10 text-center text-slate-400">
        No snapshots found.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-3xl border border-slate-800 bg-slate-900/70 shadow-xl">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-800">
          <thead className="bg-slate-950">
            <tr>
              <th className="px-5 py-4 text-left text-xs font-medium uppercase tracking-[0.18em] text-slate-500">
                Period
              </th>
              <th className="px-5 py-4 text-left text-xs font-medium uppercase tracking-[0.18em] text-slate-500">
                Orders
              </th>
              <th className="px-5 py-4 text-left text-xs font-medium uppercase tracking-[0.18em] text-slate-500">
                Revenue
              </th>
              <th className="px-5 py-4 text-left text-xs font-medium uppercase tracking-[0.18em] text-slate-500">
                Reviews
              </th>
              <th className="px-5 py-4 text-left text-xs font-medium uppercase tracking-[0.18em] text-slate-500">
                Created
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-800">
            {snapshots.map((snapshot) => (
              <tr key={snapshot.id} className="hover:bg-slate-800/40">
                <td className="px-5 py-4 text-sm text-white">
                  {snapshot.period_type}
                </td>
                <td className="px-5 py-4 text-sm text-slate-300">
                  {snapshot.total_orders}
                </td>
                <td className="px-5 py-4 text-sm text-slate-300">
                  {formatAnalyticsCurrency(snapshot.net_revenue)}
                </td>
                <td className="px-5 py-4 text-sm text-slate-300">
                  {snapshot.total_reviews}
                </td>
                <td className="px-5 py-4 text-sm text-slate-400">
                  {formatDateTime(snapshot.created_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}