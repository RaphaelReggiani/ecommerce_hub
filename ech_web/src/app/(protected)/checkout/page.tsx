"use client";

import { useMemo, useState } from "react";

import { CartSummary } from "@/features/orders/components/cart-summary";
import {
  CheckoutForm,
  type CheckoutFormValues,
} from "@/features/orders/components/checkout-form";
import { useCart } from "@/features/orders/hooks/use-cart";

const initialAddress: CheckoutFormValues = {
  full_name: "",
  address_line: "",
  city: "",
  state: "",
  country: "",
  postal_code: "",
  phone: "",
};

function calculateShippingCost(params: {
  country: string;
  state: string;
  itemCount: number;
  subtotal: number;
}) {
  const { country, state, itemCount, subtotal } = params;

  if (itemCount <= 0 || subtotal <= 0) {
    return 0;
  }

  const normalizedCountry = country.trim().toLowerCase();
  const normalizedState = state.trim().toLowerCase();

  if (!normalizedCountry) {
    return 20;
  }

  if (
    normalizedCountry === "united states" ||
    normalizedCountry === "usa" ||
    normalizedCountry === "us"
  ) {
    const base = normalizedState === "new york" ? 18 : 22;
    return base + itemCount * 5;
  }

  if (
    normalizedCountry === "brazil" ||
    normalizedCountry === "brasil" ||
    normalizedCountry === "br"
  ) {
    const base =
      normalizedState === "são paulo" ||
      normalizedState === "sao paulo" ||
      normalizedState === "sp"
        ? 28
        : 35;

    return base + itemCount * 7;
  }

  return 50 + itemCount * 10;
}

export default function CheckoutPage() {
  const { items, subtotal } = useCart();
  const [address, setAddress] = useState<CheckoutFormValues>(initialAddress);

  const itemCount = items.reduce((total, item) => total + item.quantity, 0);

  const shippingCost = useMemo(
    () =>
      calculateShippingCost({
        country: address.country,
        state: address.state,
        itemCount,
        subtotal,
      }),
    [address.country, address.state, itemCount, subtotal],
  );

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
        <CheckoutForm values={address} onChange={setAddress} />

        <div>
          <CartSummary
            items={items}
            subtotal={subtotal}
            shippingCost={shippingCost}
            showCheckoutButton={false}
          />
        </div>
      </section>
    </div>
  );
}