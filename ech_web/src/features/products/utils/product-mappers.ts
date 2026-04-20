import type {
  ProductCreateInput,
  ProductDetail,
  ProductListItem,
} from "@/features/products/types/product";

import type { ProductSchemaValues } from "@/features/products/schemas/product-schema";

/*
|--------------------------------------------------------------------------
| API / MEDIA URL RESOLUTION
|--------------------------------------------------------------------------
*/

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

const API_ORIGIN = API_BASE_URL.replace(/\/api\/v1\/?$/, "");

function toAbsoluteMediaUrl(url?: string | null): string {
  if (!url) return "";

  if (url.startsWith("http://") || url.startsWith("https://")) {
    return url;
  }

  return `${API_ORIGIN}${url}`;
}

/*
|--------------------------------------------------------------------------
| Product Form Mapper
|--------------------------------------------------------------------------
*/

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

/*
|--------------------------------------------------------------------------
| Product Image Normalization
|--------------------------------------------------------------------------
*/

export function normalizeProductListItem(
  product: ProductListItem,
): ProductListItem {
  return {
    ...product,
    main_image: toAbsoluteMediaUrl(product.main_image),
  };
}

export function normalizeProductDetail(
  product: ProductDetail,
): ProductDetail {
  return {
    ...product,
    main_image: toAbsoluteMediaUrl(product.main_image),
    images: product.images?.map((img) => ({
      ...img,
      image: toAbsoluteMediaUrl(img.image),
    })),
  };
}

/*
|--------------------------------------------------------------------------
| Price helpers
|--------------------------------------------------------------------------
*/

export function getDisplayPrice(product: ProductListItem | ProductDetail) {
  return product.discount_price ?? product.price;
}