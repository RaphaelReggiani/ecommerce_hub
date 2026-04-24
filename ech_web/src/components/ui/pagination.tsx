type PaginationProps = {
  page: number;
  hasNext?: boolean;
  hasPrevious?: boolean;
  onNext: () => void;
  onPrevious: () => void;
};

export function Pagination({
  page,
  hasNext = false,
  hasPrevious = false,
  onNext,
  onPrevious,
}: PaginationProps) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-2xl border border-slate-800 bg-slate-900/70 px-4 py-3">
      <button
        type="button"
        disabled={!hasPrevious}
        onClick={onPrevious}
        className="rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-blue-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
      >
        Previous
      </button>

      <span className="text-sm text-slate-400">Page {page}</span>

      <button
        type="button"
        disabled={!hasNext}
        onClick={onNext}
        className="rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-blue-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
      >
        Next
      </button>
    </div>
  );
}