export const ROLES = {
  SUPERADMIN: "superadmin",
  ADMIN: "admin",
  PAYMENT_STAFF: "payment_staff",
  OPERATIONS_STAFF: "operations_staff",
  SUPPORT_STAFF: "support_staff",
  ANALYTICS_STAFF: "analytics_staff",
  CUSTOMER_USER: "customer_user",
} as const;

export type AppRole = (typeof ROLES)[keyof typeof ROLES];