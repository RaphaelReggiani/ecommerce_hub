export function generateIdempotencyKey(prefix = "ech"): string {
  const randomPart = crypto.randomUUID();
  return `${prefix}-${randomPart}`;
}

export function buildIdempotencyHeaders(prefix = "ech"): Record<string, string> {
  return {
    "Idempotency-Key": generateIdempotencyKey(prefix),
  };
}