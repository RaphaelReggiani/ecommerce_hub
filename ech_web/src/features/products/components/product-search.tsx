"use client";

import { X } from "lucide-react";

type Props = {
  value: string;
  onChange: (value: string) => void;
};

export function ProductSearch({ value, onChange }: Props) {
  return (
    <div className="relative w-full">
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search products, brands or categories..."
        className="
          w-full
          rounded-2xl
          border
          border-slate-700
          bg-slate-950
          px-5
          py-3
          pr-10
          text-sm
          text-white
          placeholder:text-slate-500
          outline-none
          transition
          focus:border-blue-500
        "
      />

      {value && (
        <button
          type="button"
          onClick={() => onChange("")}
          className="absolute right-3 top-1/2 -translate-y-1/2 rounded-lg p-1 text-slate-400 transition hover:text-white"
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
}