import type { AdminDashboardAlerts } from "@/features/admin-dashboard/types/admin-dashboard";

type AlertsListProps = {
  alerts: AdminDashboardAlerts;
};

export function AlertsList({ alerts }: AlertsListProps) {
  if (alerts.alerts.length === 0) {
    return (
      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 text-slate-400">
        No operational alerts found.
      </div>
    );
  }

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-xl font-semibold text-white">Operational Alerts</h2>
        <span className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300">
          {alerts.total_alerts} total
        </span>
      </div>

      <div className="space-y-3">
        {alerts.alerts.map((alert) => (
          <div
            key={`${alert.type}-${alert.message}`}
            className="rounded-2xl border border-slate-800 bg-slate-950 p-4"
          >
            <div className="flex items-center justify-between gap-4">
              <p className="font-medium text-white">{alert.message}</p>
              <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase tracking-wide text-slate-300">
                {alert.severity}
              </span>
            </div>

            <p className="mt-2 text-sm text-slate-400">
              Type: {alert.type} · Value: {alert.value}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}