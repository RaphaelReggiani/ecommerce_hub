import type { ReactNode } from "react";

import { cn } from "@/lib/utils/cn";
import type { StatusTone } from "@/lib/constants/statuses";

type StatusBadgeProps = {
  children: ReactNode;
  tone?: StatusTone;
  className?: string;
};

const toneClasses: Record<StatusTone, string> = {
  default: "border-slate-700 bg-slate-900 text-slate-200",
  info: "border-blue-500/30 bg-blue-500/10 text-blue-300",
  warning: "border-amber-500/30 bg-amber-500/10 text-amber-300",
  success: "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
  danger: "border-red-500/30 bg-red-500/10 text-red-300",
  muted: "border-slate-700 bg-slate-800 text-slate-400",
};

export function StatusBadge({
  children,
  tone = "default",
  className,
}: StatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-3 py-1 text-xs font-medium capitalize tracking-wide",
        toneClasses[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}