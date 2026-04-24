import type { AdminDashboardEvent } from "@/features/admin-dashboard/types/admin-dashboard";
import { formatDateTime } from "@/lib/utils/format-date";

type AdminEventsTableProps = {
  events: AdminDashboardEvent[];
};

export function AdminEventsTable({ events }: AdminEventsTableProps) {
  if (events.length === 0) {
    return (
      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 text-slate-400">
        No admin events found.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-3xl border border-slate-800 bg-slate-900/70 shadow-xl">
      <div className="border-b border-slate-800 px-6 py-5">
        <h2 className="text-xl font-semibold text-white">Admin Events</h2>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-800">
          <thead className="bg-slate-950">
            <tr>
              <th className="px-5 py-4 text-left text-xs font-medium uppercase tracking-[0.18em] text-slate-500">Event</th>
              <th className="px-5 py-4 text-left text-xs font-medium uppercase tracking-[0.18em] text-slate-500">Performed By</th>
              <th className="px-5 py-4 text-left text-xs font-medium uppercase tracking-[0.18em] text-slate-500">Created</th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-800">
            {events.map((event) => (
              <tr key={event.id} className="hover:bg-slate-800/40">
                <td className="px-5 py-4 text-sm text-white">{event.event_type}</td>
                <td className="px-5 py-4 text-sm text-slate-300">
                  {event.performed_by_name ?? event.performed_by_email ?? "-"}
                </td>
                <td className="px-5 py-4 text-sm text-slate-400">
                  {formatDateTime(event.created_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}