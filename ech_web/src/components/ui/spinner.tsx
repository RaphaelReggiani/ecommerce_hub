type SpinnerProps = {
  label?: string;
  className?: string;
};

export function Spinner({ label = "Loading...", className = "" }: SpinnerProps) {
  return (
    <div className={`flex items-center gap-3 text-slate-400 ${className}`}>
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-slate-700 border-t-blue-500" />
      <span className="text-sm">{label}</span>
    </div>
  );
}