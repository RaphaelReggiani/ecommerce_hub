export type PaginationParams = {
  page?: number;
  pageSize?: number;
};

export type PaginationMeta = {
  count: number;
  next: string | null;
  previous: string | null;
};