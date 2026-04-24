import type { ReactNode } from "react";

type MetricsGridProps = {
  children: ReactNode;
};

export function MetricsGrid({ children }: MetricsGridProps) {
  return <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">{children}</div>;
}