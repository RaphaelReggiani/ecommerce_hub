type PageTitleProps = {
  title: string;
  description?: string;
  eyebrow?: string;
  actions?: React.ReactNode;
};

export function PageTitle({
  title,
  description,
  eyebrow,
  actions,
}: PageTitleProps) {
  return (
    <div className="flex flex-col gap-4 rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl sm:flex-row sm:items-end sm:justify-between">
      <div>
        {eyebrow && (
          <p className="text-xs uppercase tracking-[0.22em] text-slate-500">
            {eyebrow}
          </p>
        )}

        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white">
          {title}
        </h1>

        {description && (
          <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">
            {description}
          </p>
        )}
      </div>

      {actions ? <div className="shrink-0">{actions}</div> : null}
    </div>
  );
}