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
    <div className="grid gap-4 md:grid-cols-3">
      <select
        value={filters.product_type ?? ""}
        onChange={(e) =>
          onChange({ ...filters, product_type: e.target.value || undefined })
        }
      >
        <option value="">All categories</option>

        {productTypes.map((type) => (
          <option key={type.value} value={type.value}>
            {type.label}
          </option>
        ))}
      </select>

      <input
        placeholder="Brand"
        value={filters.brand ?? ""}
        onChange={(e) =>
          onChange({ ...filters, brand: e.target.value || undefined })
        }
      />

      <select
        value={filters.ordering ?? "-created_at"}
        onChange={(e) =>
          onChange({ ...filters, ordering: e.target.value })
        }
      >
        {orderingOptions.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}