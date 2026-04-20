type Props = {
  inventory: number;
};

export function StockBadge({ inventory }: Props) {
  let label = "";
  let styles = "";

  if (inventory <= 0) {
    label = "Out of stock";
    styles =
      "border-red-500/30 bg-red-500/10 text-red-400";
  } else if (inventory <= 5) {
    label = `Low stock (${inventory})`;
    styles =
      "border-yellow-500/30 bg-yellow-500/10 text-yellow-400";
  } else {
    label = `${inventory} in stock`;
    styles =
      "border-blue-500/30 bg-blue-500/10 text-blue-400";
  }

  return (
    <span
      className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-medium tracking-wide ${styles}`}
    >
      {label}
    </span>
  );
}