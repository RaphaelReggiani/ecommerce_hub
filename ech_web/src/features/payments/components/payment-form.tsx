"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { useCreatePayment } from "@/features/payments/hooks/use-create-payment";
import {
  createPaymentSchema,
  type CreatePaymentSchemaValues,
} from "@/features/payments/schemas/payment-schema";
import { ApiClientError } from "@/lib/api/error-handler";

type PaymentFormProps = {
  orderId: string;
  onSuccess?: () => void;
};

const paymentMethods = [
  { value: "credit_card", label: "Credit card" },
  { value: "debit_card", label: "Debit card" },
  { value: "pix", label: "Pix" },
  { value: "bank_slip", label: "Bank slip" },
  { value: "wallet", label: "Wallet" },
] as const;

export function PaymentForm({ orderId, onSuccess }: PaymentFormProps) {
  const createPaymentMutation = useCreatePayment();
  const [formError, setFormError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreatePaymentSchemaValues>({
    resolver: zodResolver(createPaymentSchema),
    defaultValues: {
      order_id: orderId,
      method: "credit_card",
      payment_reference: "",
    },
  });

  async function onSubmit(values: CreatePaymentSchemaValues) {
    setFormError(null);

    try {
      await createPaymentMutation.mutateAsync(values);
      onSuccess?.();
    } catch (error) {
      if (error instanceof ApiClientError) {
        setFormError(error.message);
        return;
      }

      setFormError("Unable to create payment right now.");
    }
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl"
    >
      <div className="mb-6">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
          Payment
        </p>
        <h2 className="mt-2 text-2xl font-semibold text-white">
          Create payment
        </h2>
      </div>

      {formError ? (
        <div className="mb-4 rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {formError}
        </div>
      ) : null}

      <input type="hidden" {...register("order_id")} />

      <div className="mb-4">
        <label className="mb-2 block text-sm font-medium text-slate-300">
          Method
        </label>
        <select
          {...register("method")}
          className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
        >
          {paymentMethods.map((method) => (
            <option key={method.value} value={method.value}>
              {method.label}
            </option>
          ))}
        </select>
        {errors.method ? (
          <p className="mt-2 text-sm text-red-400">{errors.method.message}</p>
        ) : null}
      </div>

      <div className="mb-6">
        <label className="mb-2 block text-sm font-medium text-slate-300">
          Payment reference
        </label>
        <input
          type="text"
          {...register("payment_reference")}
          className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
          placeholder="Optional reference"
        />
        {errors.payment_reference ? (
          <p className="mt-2 text-sm text-red-400">
            {errors.payment_reference.message}
          </p>
        ) : null}
      </div>

      <button
        type="submit"
        disabled={createPaymentMutation.isPending}
        className="w-full rounded-2xl bg-blue-600 px-4 py-3 font-medium text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {createPaymentMutation.isPending ? "Creating payment..." : "Create payment"}
      </button>
    </form>
  );
}