type KpiCardProps = {
  title: string;
  value: string | number;
  description?: string;
};

export function KpiCard({ title, value, description }: KpiCardProps) {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
      <p className="text-xs font-medium uppercase tracking-[0.22em] text-slate-500">
        {title}
      </p>

      <p className="mt-4 text-3xl font-semibold text-white">{value}</p>

      {description && (
        <p className="mt-3 text-sm leading-6 text-slate-400">{description}</p>
      )}
    </div>
  );
}