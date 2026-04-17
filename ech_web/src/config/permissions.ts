import { ROLES } from "@/lib/constants/roles";

export const PERMISSIONS = {
  adminAccess: [
    ROLES.SUPERADMIN,
    ROLES.ADMIN,
    ROLES.PAYMENT_STAFF,
    ROLES.OPERATIONS_STAFF,
    ROLES.SUPPORT_STAFF,
    ROLES.ANALYTICS_STAFF,
  ],

  analyticsAccess: [
    ROLES.SUPERADMIN,
    ROLES.ADMIN,
    ROLES.ANALYTICS_STAFF,
  ],

  paymentAccess: [
    ROLES.SUPERADMIN,
    ROLES.ADMIN,
    ROLES.PAYMENT_STAFF,
  ],

  operationsAccess: [
    ROLES.SUPERADMIN,
    ROLES.ADMIN,
    ROLES.OPERATIONS_STAFF,
  ],

  supportAccess: [
    ROLES.SUPERADMIN,
    ROLES.ADMIN,
    ROLES.SUPPORT_STAFF,
  ],

  customerOnly: [
    ROLES.CUSTOMER_USER,
  ],

  staffOnly: [
    ROLES.SUPERADMIN,
    ROLES.ADMIN,
    ROLES.PAYMENT_STAFF,
    ROLES.OPERATIONS_STAFF,
    ROLES.SUPPORT_STAFF,
    ROLES.ANALYTICS_STAFF,
  ],
} as const;