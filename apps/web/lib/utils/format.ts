export function formatShortId(id: string, prefix: "case" | "pay" | "corr" = "case"): string {
  if (!id) return "N/A";
  const clean = id.replace(/-/g, "");
  // Take last 4-6 chars
  const suffix = clean.length > 6 ? clean.slice(-4) : clean;
  return `${prefix}_${suffix}`;
}

export function formatCurrency(amountMinor: number = 0): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format((amountMinor || 0) / 100);
}
