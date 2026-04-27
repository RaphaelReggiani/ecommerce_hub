"use client";

import { useRouter } from "next/navigation";

import { useCart } from "@/features/orders/hooks/use-cart";
import { useCreateOrder } from "@/features/orders/hooks/use-create-order";
import type { CreateOrderInput } from "@/features/orders/types/checkout";

export type CheckoutFormValues = {
  full_name: string;
  address_line: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
  phone: string;
};

type CheckoutFormProps = {
  values: CheckoutFormValues;
  onChange: (values: CheckoutFormValues) => void;
};

export function CheckoutForm({ values, onChange }: CheckoutFormProps) {
  const router = useRouter();
  const { items, clear } = useCart();
  const createOrderMutation = useCreateOrder();

  function handleChange(field: keyof CheckoutFormValues, value: string) {
    onChange({ ...values, [field]: value });
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!items.length) {
      return;
    }

    const payload: CreateOrderInput = {
      items: items.map((item) => ({
        product_id: item.product_id,
        quantity: item.quantity,
      })),
      address: {
        full_name: values.full_name,
        address_line: values.address_line,
        city: values.city,
        state: values.state,
        country: values.country,
        postal_code: values.postal_code,
        phone: values.phone || "",
      },
    };

    const order = await createOrderMutation.mutateAsync(payload);
    clear();
    router.push(`/account/orders/${order.id}`);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl">
        <div className="mb-6">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Checkout
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-white">
            Shipping address
          </h2>
        </div>

        {createOrderMutation.isError && (
          <div className="mb-6 rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
            Unable to place the order right now.
          </div>
        )}

        <div className="grid gap-4 md:grid-cols-2">
          <input
            value={values.full_name}
            onChange={(e) => handleChange("full_name", e.target.value)}
            placeholder="Full name"
            className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
          />

          <input
            value={values.phone}
            onChange={(e) => handleChange("phone", e.target.value)}
            placeholder="Phone"
            className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
          />

          <input
            value={values.address_line}
            onChange={(e) => handleChange("address_line", e.target.value)}
            placeholder="Address line"
            className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500 md:col-span-2"
          />

          <input
            value={values.city}
            onChange={(e) => handleChange("city", e.target.value)}
            placeholder="City"
            className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
          />

          <input
            value={values.state}
            onChange={(e) => handleChange("state", e.target.value)}
            placeholder="State"
            className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
          />

          <input
            value={values.country}
            onChange={(e) => handleChange("country", e.target.value)}
            placeholder="Country"
            className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
          />

          <input
            value={values.postal_code}
            onChange={(e) => handleChange("postal_code", e.target.value)}
            placeholder="Postal code"
            className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
          />
        </div>

        <button
          type="submit"
          disabled={createOrderMutation.isPending}
          className="mt-6 inline-flex w-full items-center justify-center rounded-2xl bg-blue-600 px-5 py-3 text-sm font-medium text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {createOrderMutation.isPending ? "Placing order..." : "Place order"}
        </button>
      </div>
    </form>
  );
}