import type { AdminDashboardLogDetail } from "@/features/admin-dashboard/types/admin-dashboard";
import { formatDateTime } from "@/lib/utils/format-date";

type AdminLogDetailProps = {
  log: AdminDashboardLogDetail;
};

export function AdminLogDetail({ log }: AdminLogDetailProps) {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
      <h2 className="text-xl font-semibold text-white">Log Detail</h2>

      <div className="mt-5 grid gap-4 text-sm text-slate-300 md:grid-cols-2">
        <p><span className="text-slate-500">Action:</span> {log.action_type}</p>
        <p><span className="text-slate-500">Module:</span> {log.target_module ?? "-"}</p>
        <p><span className="text-slate-500">Target:</span> {log.target_object_id ?? "-"}</p>
        <p><span className="text-slate-500">Created:</span> {formatDateTime(log.created_at)}</p>
      </div>
    </div>
  );
}