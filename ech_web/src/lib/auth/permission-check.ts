import { PERMISSIONS } from "@/config/permissions";
import { ROLES, type AppRole } from "@/lib/constants/roles";

export function hasRole(userRole: string | undefined | null, role: AppRole): boolean {
  return userRole === role;
}

export function hasAnyRole(
  userRole: string | undefined | null,
  roles: readonly AppRole[],
): boolean {
  return roles.includes(userRole as AppRole);
}

export function isCustomerUser(userRole: string | undefined | null): boolean {
  return hasRole(userRole, ROLES.CUSTOMER_USER);
}

export function isStaffUser(userRole: string | undefined | null): boolean {
  return hasAnyRole(userRole, PERMISSIONS.staffOnly);
}

export function canAccessAdmin(userRole: string | undefined | null): boolean {
  return hasAnyRole(userRole, PERMISSIONS.adminAccess);
}

export function canAccessAnalytics(userRole: string | undefined | null): boolean {
  return hasAnyRole(userRole, PERMISSIONS.analyticsAccess);
}

export function canAccessPayments(userRole: string | undefined | null): boolean {
  return hasAnyRole(userRole, PERMISSIONS.paymentAccess);
}

export function canAccessOperations(userRole: string | undefined | null): boolean {
  return hasAnyRole(userRole, PERMISSIONS.operationsAccess);
}

export function canAccessSupport(userRole: string | undefined | null): boolean {
  return hasAnyRole(userRole, PERMISSIONS.supportAccess);
}