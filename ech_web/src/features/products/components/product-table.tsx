import type { ProductListItem } from "@/features/products/types/product";

type Props = {
  products: ProductListItem[];
};

export function ProductTable({ products }: Props) {
  return (
    <table className="min-w-full text-sm">
      <thead>
        <tr>
          <th>Name</th>
          <th>Brand</th>
          <th>Price</th>
          <th>Discount</th>
        </tr>
      </thead>

      <tbody>
        {products.map((product) => (
          <tr key={product.id}>
            <td>{product.name}</td>
            <td>{product.brand}</td>
            <td>{product.price}</td>
            <td>{product.discount_price ?? "-"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}