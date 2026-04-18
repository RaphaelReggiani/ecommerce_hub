import type {
  ProductCreateInput,
  ProductDetail,
  ProductListItem,
} from "@/features/products/types/product";

import type { ProductSchemaValues } from "@/features/products/schemas/product-schema";

export function mapProductFormToCreatePayload(
  values: ProductSchemaValues,
): ProductCreateInput {
  return {
    name: values.name,
    product_type: values.product_type,
    brand: values.brand,
    description: values.description,
    technical_information: values.technical_information,
    price: values.price.toFixed(2),
    discount_price:
      values.discount_price === null || values.discount_price === undefined
        ? null
        : values.discount_price.toFixed(2),
    inventory: values.inventory,
  };
}

export function getDisplayPrice(product: ProductListItem | ProductDetail) {
  return product.discount_price ?? product.price;
}