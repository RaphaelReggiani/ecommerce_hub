"use client";

import { useParams } from "next/navigation";

import { OrderDetailCard } from "@/features/orders/components/order-detail-card";
import { useOrder } from "@/features/orders/hooks/use-order";

export default function AccountOrderDetailPage() {
  const params = useParams();
  const orderId = typeof params.id === "string" ? params.id : "";

  const { data: order, isLoading, isError } = useOrder(orderId);

  if (isLoading) {
    return (
      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-10 text-center text-slate-400 shadow-xl">
        Loading order details...
      </div>
    );
  }

  if (isError || !order) {
    return (
      <div className="rounded-3xl border border-red-500/20 bg-red-500/10 p-10 text-center text-red-300 shadow-xl">
        Unable to load this order.
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <section className="rounded-[2rem] border border-slate-800 bg-gradient-to-r from-slate-950 via-slate-900 to-blue-950 p-8 shadow-2xl lg:p-10">
        <span className="inline-flex rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1.5 text-xs font-medium uppercase tracking-[0.24em] text-blue-400">
          Order details
        </span>

        <h1 className="mt-4 text-3xl font-semibold text-white md:text-4xl">
          Order {order.id.slice(0, 8)}...
        </h1>

        <p className="mt-4 max-w-3xl text-sm leading-8 text-slate-300">
          Review the complete order information, purchased items, totals,
          shipping address, and lifecycle updates for this purchase.
        </p>
      </section>

      <OrderDetailCard order={order} />
    </div>
  );
}