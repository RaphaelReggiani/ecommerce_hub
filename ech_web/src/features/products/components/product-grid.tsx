import type { ProductListItem } from "@/features/products/types/product";
import { ProductCard } from "@/features/products/components/product-card";

type ProductGridProps = {
  products: ProductListItem[];
};

export function ProductGrid({ products }: ProductGridProps) {
  if (!products.length) {
    return (
      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-12 text-center text-slate-400 shadow-xl">
        No products found.
      </div>
    );
  }

  return (
    <div
      className="
        grid
        gap-6
        sm:grid-cols-2
        md:grid-cols-3
        lg:grid-cols-4
        xl:grid-cols-5
        2xl:grid-cols-6
      "
    >
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}