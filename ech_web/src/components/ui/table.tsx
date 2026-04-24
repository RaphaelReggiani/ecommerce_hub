import type { ReactNode, TableHTMLAttributes } from "react";

type TableProps = TableHTMLAttributes<HTMLTableElement> & {
  children: ReactNode;
};

export function Table({ children, className = "", ...props }: TableProps) {
  return (
    <div className="overflow-x-auto rounded-3xl border border-slate-800">
      <table
        className={`min-w-full divide-y divide-slate-800 text-sm ${className}`}
        {...props}
      >
        {children}
      </table>
    </div>
  );
}

export function TableHead({ children }: { children: ReactNode }) {
  return <thead className="bg-slate-950">{children}</thead>;
}

export function TableBody({ children }: { children: ReactNode }) {
  return <tbody className="divide-y divide-slate-800">{children}</tbody>;
}

export function TableRow({ children }: { children: ReactNode }) {
  return <tr className="transition hover:bg-slate-800/40">{children}</tr>;
}

export function TableHeaderCell({ children }: { children: ReactNode }) {
  return (
    <th className="px-5 py-4 text-left text-xs font-medium uppercase tracking-[0.18em] text-slate-500">
      {children}
    </th>
  );
}

export function TableCell({ children }: { children: ReactNode }) {
  return <td className="px-5 py-4 text-slate-300">{children}</td>;
}