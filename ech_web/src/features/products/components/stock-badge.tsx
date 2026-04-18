type Props = {
  inventory: number;
};

export function StockBadge({ inventory }: Props) {
  const isOut = inventory <= 0;

  return (
    <span
      className={`px-2 py-1 text-xs rounded ${
        isOut
          ? "bg-red-500/20 text-red-400"
          : "bg-blue-500/20 text-blue-400"
      }`}
    >
      {isOut ? "Out of stock" : `${inventory} in stock`}
    </span>
  );
}