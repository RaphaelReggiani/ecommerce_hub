export const notificationQueryKeys = {
  all: ["notifications"] as const,

  list: (filters?: Record<string, unknown>) =>
    ["notifications", "list", filters ?? {}] as const,

  detail: (id: string) =>
    ["notifications", "detail", id] as const,
};