"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { useCreateShipment } from "@/features/shipping/hooks/use-create-shipment";
import {
  createShipmentSchema,
  type CreateShipmentSchemaValues,
} from "@/features/shipping/schemas/shipment-schema";
import { ApiClientError } from "@/lib/api/error-handler";

type ShipmentFormProps = {
  orderId: string;
  onSuccess?: () => void;
};

const shippingMethods = [
  { value: "standard", label: "Standard" },
  { value: "express", label: "Express" },
  { value: "same_day", label: "Same day" },
  { value: "pickup_point", label: "Pickup point" },
] as const;

export function ShipmentForm({ orderId, onSuccess }: ShipmentFormProps) {
  const createShipmentMutation = useCreateShipment();
  const [formError, setFormError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateShipmentSchemaValues>({
    resolver: zodResolver(createShipmentSchema),
    defaultValues: {
      order_id: orderId,
      shipping_method: "standard",
      address_data: {
        full_name: "",
        address_line: "",
        city: "",
        state: "",
        country: "",
        postal_code: "",
        phone: "",
        delivery_instructions: "",
      },
      shipping_cost: "0.00",
      currency: "USD",
      carrier_name: "",
      tracking_code: "",
      external_reference: "",
      estimated_delivery_date: "",
    },
  });

  async function onSubmit(values: CreateShipmentSchemaValues) {
    setFormError(null);

    try {
      await createShipmentMutation.mutateAsync(values);
      onSuccess?.();
    } catch (error) {
      if (error instanceof ApiClientError) {
        setFormError(error.message);
        return;
      }

      setFormError("Unable to create shipment right now.");
    }
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl"
    >
      <div className="mb-6">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
          Shipment
        </p>
        <h2 className="mt-2 text-2xl font-semibold text-white">
          Create shipment
        </h2>
      </div>

      {formError ? (
        <div className="mb-4 rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {formError}
        </div>
      ) : null}

      <input type="hidden" {...register("order_id")} />

      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-300">
            Shipping method
          </label>
          <select
            {...register("shipping_method")}
            className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
          >
            {shippingMethods.map((method) => (
              <option key={method.value} value={method.value}>
                {method.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-slate-300">
            Carrier name
          </label>
          <input
            type="text"
            {...register("carrier_name")}
            className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-slate-300">
            Shipping cost
          </label>
          <input
            type="text"
            {...register("shipping_cost")}
            className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-slate-300">
            Currency
          </label>
          <input
            type="text"
            {...register("currency")}
            className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
          />
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <input
          type="text"
          placeholder="Full name"
          {...register("address_data.full_name")}
          className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
        />
        <input
          type="text"
          placeholder="Address line"
          {...register("address_data.address_line")}
          className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
        />
        <input
          type="text"
          placeholder="City"
          {...register("address_data.city")}
          className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
        />
        <input
          type="text"
          placeholder="State"
          {...register("address_data.state")}
          className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
        />
        <input
          type="text"
          placeholder="Country"
          {...register("address_data.country")}
          className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
        />
        <input
          type="text"
          placeholder="Postal code"
          {...register("address_data.postal_code")}
          className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500"
        />
      </div>

      {(errors.address_data?.full_name ||
        errors.address_data?.address_line ||
        errors.address_data?.city ||
        errors.address_data?.state ||
        errors.address_data?.country ||
        errors.address_data?.postal_code) && (
        <p className="mt-3 text-sm text-red-400">
          Please fill in all required address fields.
        </p>
      )}

      <button
        type="submit"
        disabled={createShipmentMutation.isPending}
        className="mt-6 w-full rounded-2xl bg-blue-600 px-4 py-3 font-medium text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {createShipmentMutation.isPending ? "Creating shipment..." : "Create shipment"}
      </button>
    </form>
  );
}