"use client";

import type {
  ProductFiltersInput,
  ProductOrderingOption,
  ProductTypeOption,
} from "@/features/products/types/product-filters";

type Props = {
  filters: ProductFiltersInput;
  productTypes: ProductTypeOption[];
  orderingOptions: ProductOrderingOption[];
  onChange: (filters: ProductFiltersInput) => void;
};

export function ProductFilters({
  filters,
  productTypes,
  orderingOptions,
  onChange,
}: Props) {
  return (
    <div className="space-y-5">
      <div>
        <label className="mb-2 block text-sm font-medium text-slate-300">
          Category
        </label>
        <select
          value={filters.product_type ?? ""}
          onChange={(e) =>
            onChange({
              ...filters,
              product_type: e.target.value || undefined,
            })
          }
          className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-500"
        >
          <option value="">All categories</option>

          {productTypes.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="mb-2 block text-sm font-medium text-slate-300">
          Brand
        </label>
        <input
          placeholder="Type a brand"
          value={filters.brand ?? ""}
          onChange={(e) =>
            onChange({
              ...filters,
              brand: e.target.value || undefined,
            })
          }
          className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white placeholder:text-slate-500 outline-none transition focus:border-blue-500"
        />
      </div>

      <div>
        <label className="mb-2 block text-sm font-medium text-slate-300">
          Sort by
        </label>
        <select
          value={filters.ordering ?? "-created_at"}
          onChange={(e) =>
            onChange({
              ...filters,
              ordering: e.target.value,
            })
          }
          className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-500"
        >
          {orderingOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}