"use client";

import { useParams } from "next/navigation";

import { useOrder } from "@/features/orders/hooks/use-order";
import { OrderDetailCard } from "@/features/orders/components/order-detail-card";

export default function AccountOrderDetailPage() {
  const params = useParams();
  const orderId = typeof params.id === "string" ? params.id : "";

  const { data: order, isLoading, isError } = useOrder(orderId);

  if (isLoading) {
    return (
      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-10 text-center text-slate-400">
        Loading order details...
      </div>
    );
  }

  if (isError || !order) {
    return (
      <div className="rounded-3xl border border-red-500/20 bg-red-500/10 p-10 text-center text-red-300">
        Unable to load this order.
      </div>
    );
  }

  return <OrderDetailCard order={order} />;
}