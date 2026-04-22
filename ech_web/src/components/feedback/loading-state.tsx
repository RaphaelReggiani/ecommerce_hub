type LoadingStateProps = {
  title?: string;
  description?: string;
};

export function LoadingState({
  title = "Loading...",
  description = "Please wait while we prepare the data for this section.",
}: LoadingStateProps) {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-10 text-center shadow-xl">
      <div className="mx-auto max-w-xl">
        <div className="mx-auto h-12 w-12 animate-spin rounded-full border-2 border-slate-700 border-t-blue-500" />
        <h2 className="mt-5 text-2xl font-semibold text-white">{title}</h2>
        <p className="mt-3 text-sm leading-6 text-slate-400">{description}</p>
      </div>
    </div>
  );
}