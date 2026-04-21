"use client";

import { CartItem } from "@/features/orders/components/cart-item";
import { CartSummary } from "@/features/orders/components/cart-summary";
import { useCart } from "@/features/orders/hooks/use-cart";

export default function CartPage() {
  const { items, subtotal, updateQuantity, removeItem } = useCart();

  function handleIncrease(productId: string) {
    const item = items.find((entry) => entry.product_id === productId);
    if (!item) return;
    updateQuantity(productId, item.quantity + 1);
  }

  function handleDecrease(productId: string) {
    const item = items.find((entry) => entry.product_id === productId);
    if (!item) return;
    updateQuantity(productId, item.quantity - 1);
  }

  return (
    <div className="space-y-8">
      <section className="rounded-[2rem] border border-slate-800 bg-gradient-to-r from-slate-950 via-slate-900 to-blue-950 p-8 shadow-2xl lg:p-10">
        <span className="inline-flex rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1.5 text-xs font-medium uppercase tracking-[0.24em] text-blue-400">
          Cart
        </span>

        <h1 className="mt-4 text-3xl font-semibold text-white md:text-4xl">
          Review your selected items
        </h1>

        <p className="mt-4 max-w-3xl text-sm leading-8 text-slate-300">
          Adjust quantities, remove products, and continue to checkout when your
          cart is ready.
        </p>
      </section>

      <section className="grid gap-8 lg:grid-cols-[1fr_380px]">
        <div className="space-y-4">
          {items.length ? (
            items.map((item) => (
              <CartItem
                key={item.product_id}
                item={item}
                onIncrease={handleIncrease}
                onDecrease={handleDecrease}
                onRemove={removeItem}
              />
            ))
          ) : (
            <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-10 text-center text-slate-400">
              Your cart is empty.
            </div>
          )}
        </div>

        <div>
          <CartSummary items={items} subtotal={subtotal} />
        </div>
      </section>
    </div>
  );
}