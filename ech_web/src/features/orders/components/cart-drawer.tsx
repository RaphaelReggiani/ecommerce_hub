"use client";

import { CartItem } from "@/features/orders/components/cart-item";
import { CartSummary } from "@/features/orders/components/cart-summary";
import type { CartItem as CartItemType } from "@/features/orders/types/cart";

type CartDrawerProps = {
  isOpen: boolean;
  items: CartItemType[];
  subtotal: number;
  onClose: () => void;
  onIncrease: (productId: string) => void;
  onDecrease: (productId: string) => void;
  onRemove: (productId: string) => void;
};

export function CartDrawer({
  isOpen,
  items,
  subtotal,
  onClose,
  onIncrease,
  onDecrease,
  onRemove,
}: CartDrawerProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[60] flex">
      <button
        type="button"
        onClick={onClose}
        className="flex-1 bg-black/70"
        aria-label="Close cart drawer"
      />

      <div className="h-full w-full max-w-xl overflow-y-auto border-l border-slate-800 bg-slate-950 p-6 shadow-2xl">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
              Cart
            </p>
            <h2 className="mt-1 text-2xl font-semibold text-white">
              Your items
            </h2>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-slate-500 hover:text-white"
          >
            Close
          </button>
        </div>

        <div className="space-y-4">
          {items.length ? (
            items.map((item) => (
              <CartItem
                key={item.product_id}
                item={item}
                onIncrease={onIncrease}
                onDecrease={onDecrease}
                onRemove={onRemove}
              />
            ))
          ) : (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-8 text-center text-slate-400">
              Your cart is empty.
            </div>
          )}
        </div>

        <div className="mt-6">
          <CartSummary items={items} subtotal={subtotal} />
        </div>
      </div>
    </div>
  );
}