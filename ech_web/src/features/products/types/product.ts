export type ProductImage = {
  id: string;
  image: string;
  order: number;
};

export type ProductListItem = {
  id: string;
  name: string;
  brand: string;
  price: string;
  discount_price: string | null;
  main_image: string | null;
};

export type ProductDetail = {
  id: string;
  name: string;
  product_type: string;
  brand: string;
  description: string;
  technical_information: string;
  price: string;
  discount_price: string | null;
  has_discount: boolean;
  inventory: number;
  main_image: string | null;
  images: readonly ProductImage[];
  created_at: string;
};

/*
|--------------------------------------------------------------------------
| Product inputs (API)
|--------------------------------------------------------------------------
*/

export type ProductCreateInput = {
  name: string;
  product_type: string;
  brand: string;
  description: string;
  technical_information: string;
  price: string;
  discount_price?: string | null;
  inventory: number;
};

export type ProductUpdateInput = Partial<{
  name: string;
  brand: string;
  description: string;
  technical_information: string;
  price: string;
  discount_price: string | null;
}>;

/*
|--------------------------------------------------------------------------
| Derived types used by other modules
|--------------------------------------------------------------------------
*/

/**
 * Minimal product information required
 * to create a cart item.
 */
export type ProductForCart = Pick<
  ProductDetail,
  | "id"
  | "name"
  | "brand"
  | "product_type"
  | "price"
  | "discount_price"
  | "main_image"
  | "inventory"
>;