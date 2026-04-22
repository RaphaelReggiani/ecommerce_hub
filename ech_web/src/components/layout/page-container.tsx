import type { ReactNode } from "react";

type PageContainerProps = {
  children: ReactNode;
  className?: string;
};

export function PageContainer({
  children,
  className = "",
}: PageContainerProps) {
  return <div className={`space-y-8 ${className}`.trim()}>{children}</div>;
}