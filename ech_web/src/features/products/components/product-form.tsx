"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import { productTypeOptions } from "@/features/products/api/product-filters";
import {
  productSchema,
  type ProductSchemaValues,
} from "@/features/products/schemas/product-schema";

type ProductFormProps = {
  onSubmit: (values: ProductSchemaValues) => Promise<void> | void;
};

export function ProductForm({ onSubmit }: ProductFormProps) {
  const form = useForm<ProductSchemaValues>({
    resolver: zodResolver(productSchema),
    defaultValues: {
      name: "",
      product_type: "PHONE",
      brand: "",
      description: "",
      technical_information: "",
      price: 0,
      discount_price: null,
      inventory: 0,
    },
  });

  return (
    <form
      onSubmit={form.handleSubmit(onSubmit)}
      className="space-y-4 rounded-2xl border border-slate-800 bg-slate-900 p-6"
    >
      <div>
        <label className="mb-2 block text-sm text-slate-300">Name</label>
        <input
          {...form.register("name")}
          placeholder="Name"
          className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white"
        />
        {form.formState.errors.name && (
          <p className="mt-2 text-sm text-red-400">
            {form.formState.errors.name.message}
          </p>
        )}
      </div>

      <div>
        <label className="mb-2 block text-sm text-slate-300">Type</label>
        <select
          {...form.register("product_type")}
          className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white"
        >
          {productTypeOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {form.formState.errors.product_type && (
          <p className="mt-2 text-sm text-red-400">
            {form.formState.errors.product_type.message}
          </p>
        )}
      </div>

      <div>
        <label className="mb-2 block text-sm text-slate-300">Brand</label>
        <input
          {...form.register("brand")}
          placeholder="Brand"
          className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white"
        />
        {form.formState.errors.brand && (
          <p className="mt-2 text-sm text-red-400">
            {form.formState.errors.brand.message}
          </p>
        )}
      </div>

      <div>
        <label className="mb-2 block text-sm text-slate-300">Description</label>
        <textarea
          {...form.register("description")}
          placeholder="Description"
          className="min-h-28 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white"
        />
        {form.formState.errors.description && (
          <p className="mt-2 text-sm text-red-400">
            {form.formState.errors.description.message}
          </p>
        )}
      </div>

      <div>
        <label className="mb-2 block text-sm text-slate-300">
          Technical information
        </label>
        <textarea
          {...form.register("technical_information")}
          placeholder="Technical info"
          className="min-h-28 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white"
        />
        {form.formState.errors.technical_information && (
          <p className="mt-2 text-sm text-red-400">
            {form.formState.errors.technical_information.message}
          </p>
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div>
          <label className="mb-2 block text-sm text-slate-300">Price</label>
          <input
            type="number"
            step="0.01"
            {...form.register("price", {
              setValueAs: (value) => (value === "" ? 0 : Number(value)),
            })}
            placeholder="Price"
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white"
          />
          {form.formState.errors.price && (
            <p className="mt-2 text-sm text-red-400">
              {form.formState.errors.price.message}
            </p>
          )}
        </div>

        <div>
          <label className="mb-2 block text-sm text-slate-300">Discount price</label>
          <input
            type="number"
            step="0.01"
            {...form.register("discount_price", {
              setValueAs: (value) =>
                value === "" || value === null ? null : Number(value),
            })}
            placeholder="Discount price"
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white"
          />
          {form.formState.errors.discount_price && (
            <p className="mt-2 text-sm text-red-400">
              {form.formState.errors.discount_price.message}
            </p>
          )}
        </div>

        <div>
          <label className="mb-2 block text-sm text-slate-300">Inventory</label>
          <input
            type="number"
            {...form.register("inventory", {
              setValueAs: (value) => (value === "" ? 0 : Number(value)),
            })}
            placeholder="Inventory"
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white"
          />
          {form.formState.errors.inventory && (
            <p className="mt-2 text-sm text-red-400">
              {form.formState.errors.inventory.message}
            </p>
          )}
        </div>
      </div>

      <button
        type="submit"
        className="rounded-xl bg-blue-600 px-5 py-3 font-medium text-white transition hover:bg-blue-500"
      >
        Save
      </button>
    </form>
  );
}