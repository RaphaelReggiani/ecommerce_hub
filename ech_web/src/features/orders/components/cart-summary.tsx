"use client";

import Link from "next/link";

import { formatCurrency } from "@/lib/utils/format-currency";
import type { CartItem } from "@/features/orders/types/cart";

type CartSummaryProps = {
  items: CartItem[];
  subtotal: number;
  checkoutHref?: string;
  showCheckoutButton?: boolean;
};

export function CartSummary({
  items,
  subtotal,
  checkoutHref = "/checkout",
  showCheckoutButton = true,
}: CartSummaryProps) {
  const itemCount = items.reduce((total, item) => total + item.quantity, 0);

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
      <div className="space-y-4">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Cart summary
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-white">Review cart</h2>
        </div>

        <div className="space-y-3 rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <div className="flex items-center justify-between text-sm text-slate-400">
            <span>Items</span>
            <span>{itemCount}</span>
          </div>

          <div className="flex items-center justify-between text-sm text-slate-400">
            <span>Products</span>
            <span>{items.length}</span>
          </div>

          <div className="flex items-center justify-between border-t border-slate-800 pt-3">
            <span className="text-base font-medium text-white">Subtotal</span>
            <span className="text-2xl font-semibold text-blue-400">
              {formatCurrency(subtotal)}
            </span>
          </div>
        </div>

        {showCheckoutButton && (
          <Link
            href={checkoutHref}
            className="inline-flex w-full items-center justify-center rounded-2xl bg-blue-600 px-5 py-3 text-sm font-medium text-white transition hover:bg-blue-500"
          >
            Proceed to checkout
          </Link>
        )}
      </div>
    </div>
  );
}