"use client";

import { useMemo, useState } from "react";

import {
  productOrderingOptions,
  productTypeOptions,
} from "@/features/products/api/product-filters";
import { ProductFilters } from "@/features/products/components/product-filters";
import { ProductGrid } from "@/features/products/components/product-grid";
import { ProductSearch } from "@/features/products/components/product-search";
import { useProducts } from "@/features/products/hooks/use-products";
import type { ProductFiltersInput } from "@/features/products/types/product-filters";

export default function ProductsPage() {
  const [filters, setFilters] = useState<ProductFiltersInput>({
    page: 1,
    ordering: "-created_at",
  });

  const [searchValue, setSearchValue] = useState("");

  const mergedFilters = useMemo<ProductFiltersInput>(() => {
    return {
      ...filters,
      search: searchValue || undefined,
    };
  }, [filters, searchValue]);

  const { data, isLoading, isError } = useProducts(mergedFilters);

  function handleFiltersChange(nextFilters: ProductFiltersInput) {
    setFilters((current) => ({
      ...current,
      ...nextFilters,
      page: nextFilters.page ?? 1,
    }));
  }

  function handleSearchChange(value: string) {
    setSearchValue(value);
    setFilters((current) => ({
      ...current,
      page: 1,
    }));
  }

  function handlePreviousPage() {
    setFilters((current) => ({
      ...current,
      page: Math.max((current.page ?? 1) - 1, 1),
    }));
  }

  function handleNextPage() {
    setFilters((current) => ({
      ...current,
      page: (current.page ?? 1) + 1,
    }));
  }

  const products = data?.results ?? [];
  const hasPrevious = Boolean(data?.previous);
  const hasNext = Boolean(data?.next);

  return (
    <div className="min-h-screen bg-black px-6 py-10 text-gray-100">
      <div className="mx-auto max-w-7xl space-y-8">
        <section className="rounded-3xl border border-slate-800 bg-slate-900/60 p-8 shadow-xl">
          <div className="max-w-3xl space-y-3">
            <span className="inline-flex rounded-full border border-blue-500/30 bg-blue-500/10 px-3 py-1 text-xs font-medium uppercase tracking-[0.2em] text-blue-400">
              E-commerce Hub
            </span>

            <h1 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">
              Premium electronics and peripherals
            </h1>

            <p className="text-sm leading-6 text-slate-400 md:text-base">
              Explore phones, headsets, keyboards, mice, microphones, and other
              devices selected by our operations team for a clean and modern
              shopping experience.
            </p>
          </div>
        </section>

        <section className="space-y-4">
          <ProductSearch
            value={searchValue}
            onChange={handleSearchChange}
          />

          <ProductFilters
            filters={filters}
            productTypes={productTypeOptions}
            orderingOptions={productOrderingOptions}
            onChange={handleFiltersChange}
          />
        </section>

        {isLoading ? (
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-10 text-center text-slate-400">
            Loading products...
          </div>
        ) : isError ? (
          <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-10 text-center text-red-300">
            Unable to load products right now.
          </div>
        ) : (
          <>
            <ProductGrid products={products} />

            <div className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-900 px-4 py-4">
              <div className="text-sm text-slate-400">
                {typeof data?.count === "number" ? `${data.count} products found` : "Products"}
              </div>

              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={handlePreviousPage}
                  disabled={!hasPrevious}
                  className="rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-blue-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Previous
                </button>

                <span className="text-sm text-slate-400">
                  Page {filters.page ?? 1}
                </span>

                <button
                  type="button"
                  onClick={handleNextPage}
                  disabled={!hasNext}
                  className="rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-blue-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}