"use client";

import { CartSummary } from "@/features/orders/components/cart-summary";
import { CheckoutForm } from "@/features/orders/components/checkout-form";
import { useCart } from "@/features/orders/hooks/use-cart";

export default function CheckoutPage() {
  const { items, subtotal } = useCart();

  return (
    <div className="space-y-8">
      <section className="rounded-[2rem] border border-slate-800 bg-gradient-to-r from-slate-950 via-slate-900 to-blue-950 p-8 shadow-2xl lg:p-10">
        <span className="inline-flex rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1.5 text-xs font-medium uppercase tracking-[0.24em] text-blue-400">
          Checkout
        </span>

        <h1 className="mt-4 text-3xl font-semibold text-white md:text-4xl">
          Complete your order
        </h1>

        <p className="mt-4 max-w-3xl text-sm leading-8 text-slate-300">
          Confirm your shipping address and place your order securely.
        </p>
      </section>

      <section className="grid gap-8 lg:grid-cols-[1fr_380px]">
        <CheckoutForm />

        <div>
          <CartSummary items={items} subtotal={subtotal} showCheckoutButton={false} />
        </div>
      </section>
    </div>
  );
}