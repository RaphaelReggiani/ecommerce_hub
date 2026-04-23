export type UserRole =
  | "customer_user"
  | "staff_user"
  | "admin"
  | "superadmin";

/**
 * Base role checks
 */
export function isAuthenticated(role?: UserRole | null): boolean {
  return Boolean(role);
}

export function isCustomer(role?: UserRole | null): boolean {
  return role === "customer_user";
}

export function isStaff(role?: UserRole | null): boolean {
  return role === "staff_user";
}

export function isAdmin(role?: UserRole | null): boolean {
  return role === "admin";
}

export function isSuperAdmin(role?: UserRole | null): boolean {
  return role === "superadmin";
}

/**
 * Composite permissions
 */
export function canAccessAdminArea(role?: UserRole | null): boolean {
  return isAdmin(role) || isSuperAdmin(role);
}

export function canManageUsers(role?: UserRole | null): boolean {
  return isSuperAdmin(role);
}

export function canManageOrders(role?: UserRole | null): boolean {
  return isStaff(role) || isAdmin(role) || isSuperAdmin(role);
}

export function canManageReviews(role?: UserRole | null): boolean {
  return isStaff(role) || isAdmin(role) || isSuperAdmin(role);
}

export function canManageProducts(role?: UserRole | null): boolean {
  return isAdmin(role) || isSuperAdmin(role);
}

export function canViewAnalytics(role?: UserRole | null): boolean {
  return isAdmin(role) || isSuperAdmin(role);
}

/**
 * UI helpers
 */
export function shouldShowRole(role?: UserRole | null): boolean {
  return isAdmin(role) || isSuperAdmin(role);
}