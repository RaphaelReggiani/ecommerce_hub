import type {
  ProductFiltersInput,
  ProductOrderingOption,
  ProductTypeOption,
} from "@/features/products/types/product-filters";

export const productTypeOptions: ProductTypeOption[] = [
  { label: "Phone", value: "PHONE" },
  { label: "Earphone", value: "EARPHONE" },
  { label: "Headset", value: "HEADSET" },
  { label: "Mouse", value: "MOUSE" },
  { label: "Keyboard", value: "KEYBOARD" },
  { label: "Microphone", value: "MICROPHONE" },
];

export const productOrderingOptions: ProductOrderingOption[] = [
  { label: "Newest", value: "-created_at" },
  { label: "Oldest", value: "created_at" },
  { label: "Name A-Z", value: "name" },
  { label: "Name Z-A", value: "-name" },
  { label: "Price Low to High", value: "price" },
  { label: "Price High to Low", value: "-price" },
];

export const defaultProductFilters: ProductFiltersInput = {
  page: 1,
  pageSize: 12,
  ordering: "-created_at",
};