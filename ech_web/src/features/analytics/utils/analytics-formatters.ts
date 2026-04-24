import { formatCurrency } from "@/lib/utils/format-currency";
import { formatNumber } from "@/lib/utils/format-number";

export function toNumber(value: string | number | null | undefined): number {
  if (value === null || value === undefined) return 0;
  return Number(value);
}

export function formatAnalyticsCurrency(value: string | number): string {
  return formatCurrency(toNumber(value));
}

export function formatAnalyticsNumber(value: string | number): string {
  return formatNumber(toNumber(value));
}

export function formatAnalyticsPercent(value: string | number): string {
  return `${toNumber(value).toFixed(1)}%`;
}