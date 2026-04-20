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
      page: 1,
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
    <div className="min-h-screen bg-black px-4 py-8 text-gray-100 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-screen-2xl space-y-8">
        <section className="overflow-hidden rounded-3xl border border-slate-800 bg-gradient-to-r from-slate-950 via-slate-900 to-blue-950 shadow-2xl">
          <div className="grid gap-8 px-8 py-10 lg:grid-cols-[1.3fr_0.9fr] lg:px-10 lg:py-12">
            <div className="space-y-5">
              <span className="inline-flex rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1.5 text-xs font-medium uppercase tracking-[0.25em] text-blue-400">
                E-commerce Hub
              </span>

              <div className="space-y-4">
                <h1 className="max-w-3xl text-4xl font-semibold leading-tight text-white md:text-5xl">
                  Premium electronics and peripherals
                </h1>

                <p className="max-w-2xl text-base leading-7 text-slate-300">
                  Explore phones, headsets, keyboards, mice, microphones, and
                  other devices selected by our operations team for a clean,
                  modern, and high-performance shopping experience.
                </p>
              </div>

              <div className="flex flex-wrap gap-3 pt-2">
                <div className="rounded-2xl border border-slate-700 bg-slate-950/70 px-4 py-3 text-sm text-slate-300">
                  Professional-grade devices
                </div>
                <div className="rounded-2xl border border-slate-700 bg-slate-950/70 px-4 py-3 text-sm text-slate-300">
                  Staff-curated catalog
                </div>
                <div className="rounded-2xl border border-slate-700 bg-slate-950/70 px-4 py-3 text-sm text-slate-300">
                  Phones, audio, gaming, and office
                </div>
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
              <div className="rounded-3xl border border-blue-500/20 bg-blue-500/10 p-6">
                <p className="text-sm font-medium uppercase tracking-[0.2em] text-blue-300">
                  Featured offer
                </p>
                <h2 className="mt-3 text-3xl font-semibold text-white">
                  Save up to 15%
                </h2>
                <p className="mt-3 text-sm leading-6 text-slate-300">
                  Selected devices with promotional pricing and premium
                  performance for work, entertainment, and gaming.
                </p>
              </div>

              <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-6">
                <p className="text-sm font-medium uppercase tracking-[0.2em] text-slate-400">
                  Why customers choose us
                </p>

                <div className="mt-4 grid gap-4 sm:grid-cols-2">
                  <div className="rounded-2xl border border-slate-800 bg-slate-900 p-4">
                    <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                      Fast shipping
                    </p>
                    <p className="mt-2 text-lg font-semibold text-white">
                      Free shipping on selected items
                    </p>
                    <p className="mt-2 text-sm leading-6 text-slate-400">
                      Enjoy premium delivery options on selected products across the catalog.
                    </p>
                  </div>

                  <div className="rounded-2xl border border-slate-800 bg-slate-900 p-4">
                    <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                      Weekly highlights
                    </p>
                    <p className="mt-2 text-lg font-semibold text-white">
                      New arrivals this week
                    </p>
                    <p className="mt-2 text-sm leading-6 text-slate-400">
                      Discover new additions and featured products updated by our operations team.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <div className="grid gap-8 xl:grid-cols-[280px_minmax(0,1fr)]">
          <aside className="space-y-6">
            <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
              <div className="mb-5">
                <h2 className="text-xl font-semibold text-white">Filters</h2>
                <p className="mt-2 text-sm leading-6 text-slate-400">
                  Narrow the catalog by category, brand, and ordering.
                </p>
              </div>

              <ProductFilters
                filters={filters}
                productTypes={productTypeOptions}
                orderingOptions={productOrderingOptions}
                onChange={handleFiltersChange}
              />
            </div>

            <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
              <h3 className="text-lg font-semibold text-white">Why shop here</h3>
              <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-400">
                <li>Carefully selected electronics and peripherals.</li>
                <li>Professional catalog structure ready for expansion.</li>
                <li>Optimized product browsing with filters and pagination.</li>
              </ul>
            </div>
          </aside>

          <section className="space-y-6">
            <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div className="max-w-2xl">
                  <h2 className="text-2xl font-semibold text-white">
                    Browse the catalog
                  </h2>
                  <p className="mt-2 text-sm leading-6 text-slate-400">
                    Search across premium devices and find the best match for
                    your setup.
                  </p>
                </div>

                <div className="text-sm text-slate-400">
                  {typeof data?.count === "number"
                    ? `${data.count} products found`
                    : "Products"}
                </div>
              </div>

              <div className="mt-6">
                <ProductSearch
                  value={searchValue}
                  onChange={handleSearchChange}
                />
              </div>
            </div>

            {isLoading ? (
              <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-12 text-center text-slate-400 shadow-xl">
                Loading products...
              </div>
            ) : isError ? (
              <div className="rounded-3xl border border-red-500/20 bg-red-500/10 p-12 text-center text-red-300 shadow-xl">
                Unable to load products right now.
              </div>
            ) : (
              <>
                <ProductGrid products={products} />

                <div className="rounded-3xl border border-slate-800 bg-slate-900/70 px-6 py-5 shadow-xl">
                  <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                    <div className="text-sm text-slate-400">
                      {typeof data?.count === "number"
                        ? `${data.count} products found`
                        : "Products"}
                    </div>

                    <div className="flex items-center gap-3 self-start sm:self-auto">
                      <button
                        type="button"
                        onClick={handlePreviousPage}
                        disabled={!hasPrevious}
                        className="rounded-2xl border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-blue-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
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
                        className="rounded-2xl border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-blue-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
                      >
                        Next
                      </button>
                    </div>
                  </div>
                </div>
              </>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}