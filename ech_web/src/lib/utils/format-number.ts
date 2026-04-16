export function formatNumber(value?: number | string | null, locale = "en-US"): string {
  if (value === null || value === undefined || value === "") {
    return "-";
  }

  const amount = typeof value === "string" ? Number(value) : value;

  if (Number.isNaN(amount)) {
    return "-";
  }

  return new Intl.NumberFormat(locale).format(amount);
}