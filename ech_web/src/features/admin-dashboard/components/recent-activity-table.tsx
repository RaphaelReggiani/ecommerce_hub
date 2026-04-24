import type { AdminRecentActivity } from "@/features/admin-dashboard/types/admin-dashboard";
import { formatDateTime } from "@/lib/utils/format-date";

type RecentActivityTableProps = {
  activity: AdminRecentActivity;
};

export function RecentActivityTable({ activity }: RecentActivityTableProps) {
  if (activity.activities.length === 0) {
    return (
      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 text-slate-400">
        No recent activity found.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-3xl border border-slate-800 bg-slate-900/70 shadow-xl">
      <div className="border-b border-slate-800 px-6 py-5">
        <h2 className="text-xl font-semibold text-white">Recent Activity</h2>
        <p className="mt-1 text-sm text-slate-400">
          Showing {activity.activities.length} of {activity.total} recent activities.
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-800">
          <thead className="bg-slate-950">
            <tr>
              <th className="px-5 py-4 text-left text-xs font-medium uppercase tracking-[0.18em] text-slate-500">Source</th>
              <th className="px-5 py-4 text-left text-xs font-medium uppercase tracking-[0.18em] text-slate-500">Type</th>
              <th className="px-5 py-4 text-left text-xs font-medium uppercase tracking-[0.18em] text-slate-500">Status / Action</th>
              <th className="px-5 py-4 text-left text-xs font-medium uppercase tracking-[0.18em] text-slate-500">Created</th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-800">
            {activity.activities.map((item) => (
              <tr key={`${item.source}-${item.entity_id}`} className="hover:bg-slate-800/40">
                <td className="px-5 py-4 text-sm text-white">{item.source}</td>
                <td className="px-5 py-4 text-sm text-slate-300">{item.type}</td>
                <td className="px-5 py-4 text-sm text-slate-300">
                  {item.status ?? item.action_type ?? "-"}
                </td>
                <td className="px-5 py-4 text-sm text-slate-400">
                  {item.created_at ? formatDateTime(item.created_at) : "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}