"use client";

import { ReactNode } from "react";

type FiltersBarProps = {
  children: ReactNode;
};

export function FiltersBar({ children }: FiltersBarProps) {
  return (
    <div className="flex flex-wrap gap-3 rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
      {children}
    </div>
  );
}