"use client";

import Image from "next/image";

import { formatCurrency } from "@/lib/utils/format-currency";
import type { CartItem as CartItemType } from "@/features/orders/types/cart";

type CartItemProps = {
  item: CartItemType;
  onIncrease: (productId: string) => void;
  onDecrease: (productId: string) => void;
  onRemove: (productId: string) => void;
};

export function CartItem({
  item,
  onIncrease,
  onDecrease,
  onRemove,
}: CartItemProps) {
  const effectivePrice = Number(item.discount_price ?? item.unit_price);
  const totalPrice = effectivePrice * item.quantity;

  return (
    <div className="flex gap-4 rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
      <div className="relative h-24 w-24 shrink-0 overflow-hidden rounded-xl border border-slate-800 bg-slate-950">
        {item.main_image ? (
          <Image
            src={item.main_image}
            alt={item.name}
            fill
            sizes="96px"
            className="object-cover"
            unoptimized
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-xs text-slate-500">
            No image
          </div>
        )}
      </div>

      <div className="flex min-w-0 flex-1 flex-col justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            {item.brand}
          </p>
          <h3 className="mt-1 line-clamp-2 text-base font-semibold text-white">
            {item.name}
          </h3>
          <p className="mt-1 text-sm text-slate-400">{item.product_type}</p>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-950 px-2 py-2">
            <button
              type="button"
              onClick={() => onDecrease(item.product_id)}
              className="rounded-lg px-3 py-1 text-sm text-slate-300 transition hover:bg-slate-800 hover:text-white"
            >
              -
            </button>

            <span className="min-w-8 text-center text-sm font-medium text-white">
              {item.quantity}
            </span>

            <button
              type="button"
              onClick={() => onIncrease(item.product_id)}
              className="rounded-lg px-3 py-1 text-sm text-slate-300 transition hover:bg-slate-800 hover:text-white"
            >
              +
            </button>
          </div>

          <div className="text-right">
            <p className="text-sm text-slate-400">
              {formatCurrency(effectivePrice)} each
            </p>
            <p className="text-lg font-semibold text-blue-400">
              {formatCurrency(totalPrice)}
            </p>
          </div>
        </div>

        <div>
          <button
            type="button"
            onClick={() => onRemove(item.product_id)}
            className="text-sm text-red-400 transition hover:text-red-300"
          >
            Remove item
          </button>
        </div>
      </div>
    </div>
  );
}