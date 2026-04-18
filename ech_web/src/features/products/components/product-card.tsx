"use client";

import Link from "next/link";

import { formatCurrency } from "@/lib/utils/format-currency";
import type { ProductListItem } from "@/features/products/types/product";

type ProductCardProps = {
  product: ProductListItem;
};

export function ProductCard({ product }: ProductCardProps) {
  const hasDiscount =
    product.discount_price !== null &&
    Number(product.discount_price) < Number(product.price);

  return (
    <Link
      href={`/products/${product.id}`}
      className="group block rounded-2xl border border-slate-800 bg-slate-900 p-4 shadow-lg transition hover:border-blue-500/50 hover:bg-slate-900/80"
    >
      <div className="mb-4 aspect-square overflow-hidden rounded-xl bg-slate-950">
        {product.main_image ? (
          <img
            src={product.main_image}
            alt={product.name}
            className="h-full w-full object-cover transition duration-300 group-hover:scale-[1.02]"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-sm text-slate-500">
            No image
          </div>
        )}
      </div>

      <div className="space-y-2">
        <p className="text-xs uppercase tracking-wide text-slate-400">
          {product.brand}
        </p>

        <h3 className="line-clamp-2 text-lg font-semibold text-white">
          {product.name}
        </h3>

        <div className="flex items-center gap-2">
          {hasDiscount ? (
            <>
              <span className="text-lg font-semibold text-blue-400">
                {formatCurrency(product.discount_price)}
              </span>
              <span className="text-sm text-slate-500 line-through">
                {formatCurrency(product.price)}
              </span>
            </>
          ) : (
            <span className="text-lg font-semibold text-blue-400">
              {formatCurrency(product.price)}
            </span>
          )}
        </div>

        <div className="pt-2">
          <span className="inline-flex rounded-xl border border-slate-700 px-3 py-2 text-sm text-slate-300 transition group-hover:border-blue-500 group-hover:text-white">
            View details
          </span>
        </div>
      </div>
    </Link>
  );
}