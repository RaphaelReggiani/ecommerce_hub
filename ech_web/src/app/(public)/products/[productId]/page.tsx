"use client";

import { useParams } from "next/navigation";

import { StockBadge } from "@/features/products/components/stock-badge";
import { useProduct } from "@/features/products/hooks/use-product";
import { formatCurrency } from "@/lib/utils/format-currency";
import { formatDateTime } from "@/lib/utils/format-date";

export default function ProductDetailPage() {
  const params = useParams();
  const productId = typeof params.productId === "string" ? params.productId : "";

  const { data: product, isLoading, isError } = useProduct(productId);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black px-6 py-10 text-gray-100">
        <div className="mx-auto max-w-6xl rounded-2xl border border-slate-800 bg-slate-900 p-10 text-center text-slate-400">
          Loading product...
        </div>
      </div>
    );
  }

  if (isError || !product) {
    return (
      <div className="min-h-screen bg-black px-6 py-10 text-gray-100">
        <div className="mx-auto max-w-6xl rounded-2xl border border-red-500/20 bg-red-500/10 p-10 text-center text-red-300">
          Unable to load this product.
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black px-6 py-10 text-gray-100">
      <div className="mx-auto max-w-6xl space-y-8">
        <section className="grid gap-8 rounded-3xl border border-slate-800 bg-slate-900 p-8 shadow-xl lg:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-4">
            <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-950">
              {product.main_image ? (
                <img
                  src={product.main_image}
                  alt={product.name}
                  className="h-full w-full object-cover"
                />
              ) : (
                <div className="flex aspect-square items-center justify-center text-slate-500">
                  No image available
                </div>
              )}
            </div>

            {product.images.length > 0 && (
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                {product.images.map((image) => (
                  <div
                    key={image.id}
                    className="overflow-hidden rounded-xl border border-slate-800 bg-slate-950"
                  >
                    <img
                      src={image.image}
                      alt={`${product.name} image ${image.order}`}
                      className="aspect-square h-full w-full object-cover"
                    />
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="space-y-6">
            <div className="space-y-3">
              <p className="text-xs uppercase tracking-[0.2em] text-blue-400">
                {product.product_type}
              </p>

              <h1 className="text-3xl font-semibold text-white">
                {product.name}
              </h1>

              <p className="text-sm text-slate-400">
                Brand: <span className="text-slate-200">{product.brand}</span>
              </p>

              <StockBadge inventory={product.inventory} />
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
              <div className="flex items-end gap-3">
                {product.has_discount && product.discount_price ? (
                  <>
                    <span className="text-3xl font-semibold text-blue-400">
                      {formatCurrency(product.discount_price)}
                    </span>
                    <span className="text-base text-slate-500 line-through">
                      {formatCurrency(product.price)}
                    </span>
                  </>
                ) : (
                  <span className="text-3xl font-semibold text-blue-400">
                    {formatCurrency(product.price)}
                  </span>
                )}
              </div>

              <p className="mt-3 text-sm text-slate-400">
                Product published on {formatDateTime(product.created_at)}
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <button
                type="button"
                className="rounded-2xl bg-blue-600 px-5 py-4 font-medium text-white transition hover:bg-blue-500"
              >
                Buy now
              </button>

              <button
                type="button"
                className="rounded-2xl border border-slate-700 px-5 py-4 font-medium text-slate-200 transition hover:border-blue-500 hover:text-white"
              >
                Add to cart
              </button>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
              <h2 className="mb-3 text-lg font-semibold text-white">
                Description
              </h2>
              <p className="leading-7 text-slate-300">
                {product.description}
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
              <h2 className="mb-3 text-lg font-semibold text-white">
                Technical information
              </h2>
              <p className="whitespace-pre-line leading-7 text-slate-300">
                {product.technical_information}
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}