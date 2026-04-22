type ErrorStateProps = {
  title?: string;
  description?: string;
  retryLabel?: string;
  onRetry?: () => void;
};

export function ErrorState({
  title = "Unable to load this section.",
  description = "Something went wrong while loading the requested data. Please try again.",
  retryLabel = "Try again",
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="rounded-3xl border border-red-500/20 bg-red-500/10 p-10 text-center shadow-xl">
      <div className="mx-auto max-w-xl">
        <h2 className="text-2xl font-semibold text-white">{title}</h2>
        <p className="mt-3 text-sm leading-6 text-red-100/80">{description}</p>

        {onRetry ? (
          <div className="mt-6">
            <button
              type="button"
              onClick={onRetry}
              className="inline-flex items-center rounded-2xl border border-red-400/30 px-4 py-2 text-sm font-medium text-red-100 transition hover:border-red-300 hover:bg-red-500/10"
            >
              {retryLabel}
            </button>
          </div>
        ) : null}
      </div>
    </div>
  );
}