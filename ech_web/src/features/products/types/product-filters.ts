export type ProductFiltersInput = {
  search?: string;
  ordering?: string;
  product_type?: string;
  brand?: string;
  page?: number;
  pageSize?: number;
};

export type ProductTypeOption = {
  label: string;
  value: string;
};

export type ProductOrderingOption = {
  label: string;
  value: string;
};