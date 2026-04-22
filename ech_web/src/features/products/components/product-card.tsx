"use client";

import Image from "next/image";
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
      className="group flex h-full flex-col overflow-hidden rounded-3xl border border-slate-800 bg-slate-900/80 shadow-lg transition duration-300 hover:-translate-y-1 hover:border-blue-500/40 hover:bg-slate-900 hover:shadow-2xl"
    >
      <div className="relative overflow-hidden border-b border-slate-800 bg-slate-950">
        {hasDiscount && (
          <div className="absolute left-4 top-4 z-10 rounded-full border border-blue-400/20 bg-blue-500/15 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-blue-300">
            On sale
          </div>
        )}

        <div className="relative aspect-[4/3] w-full overflow-hidden">
          {product.main_image ? (
            <Image
              src={product.main_image}
              alt={product.name}
              fill
              sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
              className="object-cover transition duration-500 group-hover:scale-105"
              unoptimized
            />
          ) : (
            <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 px-6 text-center">
              <div className="space-y-2">
                <div className="mx-auto h-12 w-12 rounded-2xl border border-slate-700 bg-slate-900/80" />
                <p className="text-xs uppercase tracking-[0.25em] text-slate-500">
                  No image
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="flex flex-1 flex-col p-5">
        <div className="mb-3">
          <p className="text-[11px] font-medium uppercase tracking-[0.22em] text-slate-400">
            {product.brand}
          </p>
        </div>

        <div className="min-h-[56px]">
          <h3 className="line-clamp-2 text-base font-semibold leading-7 text-white transition group-hover:text-blue-300">
            {product.name}
          </h3>
        </div>

        <div className="mt-4 flex items-end gap-2">
          {hasDiscount ? (
            <>
              <span className="text-xl font-semibold text-blue-400">
                {formatCurrency(product.discount_price)}
              </span>
              <span className="text-sm text-slate-500 line-through">
                {formatCurrency(product.price)}
              </span>
            </>
          ) : (
            <span className="text-xl font-semibold text-blue-400">
              {formatCurrency(product.price)}
            </span>
          )}
        </div>

        <div className="mt-5 flex-1" />

        <div className="pt-4">
          <span className="inline-flex w-full items-center justify-center rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm font-medium text-slate-200 transition group-hover:border-blue-500/50 group-hover:bg-blue-500/10 group-hover:text-white">
            View details
          </span>
        </div>
      </div>
    </Link>
  );
}