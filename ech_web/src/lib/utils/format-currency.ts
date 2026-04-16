export function formatCurrency(
  value?: number | string | null,
  locale = "en-US",
  currency = "USD",
): string {
  if (value === null || value === undefined || value === "") {
    return "-";
  }

  const amount = typeof value === "string" ? Number(value) : value;

  if (Number.isNaN(amount)) {
    return "-";
  }

  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
  }).format(amount);
}