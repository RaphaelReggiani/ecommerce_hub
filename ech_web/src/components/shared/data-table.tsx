"use client";

import { ReactNode } from "react";

type Column<T> = {
  header: string;
  accessor: (row: T) => ReactNode;
};

type DataTableProps<T> = {
  data: T[];
  columns: Column<T>[];
  emptyMessage?: string;
};

export function DataTable<T>({
  data,
  columns,
  emptyMessage = "No data available.",
}: DataTableProps<T>) {
  if (!data.length) {
    return (
      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 text-center text-slate-400">
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-2xl border border-slate-800">
      <table className="w-full text-sm">
        <thead className="bg-slate-900 text-slate-400">
          <tr>
            {columns.map((col, i) => (
              <th key={i} className="px-4 py-3 text-left font-medium">
                {col.header}
              </th>
            ))}
          </tr>
        </thead>

        <tbody className="divide-y divide-slate-800">
          {data.map((row, i) => (
            <tr key={i} className="hover:bg-slate-900/60">
              {columns.map((col, j) => (
                <td key={j} className="px-4 py-3 text-slate-300">
                  {col.accessor(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}