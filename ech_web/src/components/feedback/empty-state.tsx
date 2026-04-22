import Link from "next/link";

type EmptyStateProps = {
  title?: string;
  description?: string;
  actionLabel?: string;
  actionHref?: string;
};

export function EmptyState({
  title = "Nothing to show yet.",
  description = "There is no data available for this section right now.",
  actionLabel,
  actionHref,
}: EmptyStateProps) {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-10 text-center shadow-xl">
      <div className="mx-auto max-w-xl">
        <h2 className="text-2xl font-semibold text-white">{title}</h2>
        <p className="mt-3 text-sm leading-6 text-slate-400">{description}</p>

        {actionLabel && actionHref ? (
          <div className="mt-6">
            <Link
              href={actionHref}
              className="inline-flex items-center rounded-2xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-blue-500 hover:text-white"
            >
              {actionLabel}
            </Link>
          </div>
        ) : null}
      </div>
    </div>
  );
}