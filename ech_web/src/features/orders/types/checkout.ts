export type CreateOrderItemInput = {
  product_id: string;
  quantity: number;
};

export type CreateOrderAddressInput = {
  full_name: string;
  address_line: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
  phone?: string;
};

export type CreateOrderInput = {
  items: CreateOrderItemInput[];
  address: CreateOrderAddressInput;
  idempotency_key?: string;
};