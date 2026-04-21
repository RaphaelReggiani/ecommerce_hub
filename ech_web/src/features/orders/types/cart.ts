export type CartItem = {
  product_id: string;
  name: string;
  brand: string;
  product_type: string;
  main_image: string | null;
  unit_price: string;
  discount_price: string | null;
  quantity: number;
  max_quantity?: number;
};

export type CartState = {
  items: CartItem[];
};