import type { ReactNode } from "react";

type BadgeTone = "default" | "info" | "warning" | "success" | "danger" | "muted";

type BadgeProps = {
  children: ReactNode;
  tone?: BadgeTone;
  className?: string;
};

const tones: Record<BadgeTone, string> = {
  default: "border-slate-700 bg-slate-900 text-slate-300",
  info: "border-blue-500/40 bg-blue-500/10 text-blue-300",
  warning: "border-yellow-500/40 bg-yellow-500/10 text-yellow-300",
  success: "border-emerald-500/40 bg-emerald-500/10 text-emerald-300",
  danger: "border-red-500/40 bg-red-500/10 text-red-300",
  muted: "border-slate-700 bg-slate-950 text-slate-400",
};

export function Badge({ children, tone = "default", className = "" }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-medium ${tones[tone]} ${className}`}
    >
      {children}
    </span>
  );
}