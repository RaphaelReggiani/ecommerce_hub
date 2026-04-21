import { PERMISSIONS } from "@/config/permissions";
import {
  adminRoutePrefixes,
  protectedRoutePrefixes,
  publicRoutePrefixes,
  routes,
} from "@/config/routes";
import type { SessionUser } from "@/types/common";

type UserRole = SessionUser["role"];

function normalizePathname(pathname: string): string {
  if (!pathname) {
    return "/";
  }

  if (pathname === "/") {
    return "/";
  }

  return pathname.endsWith("/") ? pathname.slice(0, -1) : pathname;
}

function matchesPrefix(pathname: string, prefix: string): boolean {
  const normalizedPathname = normalizePathname(pathname);
  const normalizedPrefix = normalizePathname(prefix);

  if (normalizedPrefix === "/") {
    return normalizedPathname === "/";
  }

  return (
    normalizedPathname === normalizedPrefix ||
    normalizedPathname.startsWith(`${normalizedPrefix}/`)
  );
}

export function isPublicRoute(pathname: string): boolean {
  return publicRoutePrefixes.some((prefix) => matchesPrefix(pathname, prefix));
}

export function isProtectedRoute(pathname: string): boolean {
  return protectedRoutePrefixes.some((prefix) => matchesPrefix(pathname, prefix));
}

export function isAdminRoute(pathname: string): boolean {
  return adminRoutePrefixes.some((prefix) => matchesPrefix(pathname, prefix));
}

export function isAuthScreen(pathname: string): boolean {
  const normalized = normalizePathname(pathname);

  const authRoutes: readonly string[] = [
    routes.public.login,
    routes.public.register,
    routes.public.forgotPassword,
    routes.public.resetPassword,
  ];

  return authRoutes.includes(normalized);
}

export function hasRequiredRole(
  userRole: UserRole | null | undefined,
  allowedRoles: readonly string[],
): boolean {
  if (!userRole) {
    return false;
  }

  return allowedRoles.includes(userRole);
}

export function canAccessAdmin(userRole: UserRole | null | undefined): boolean {
  return hasRequiredRole(userRole, PERMISSIONS.adminAccess);
}

export function canAccessAnalytics(userRole: UserRole | null | undefined): boolean {
  return hasRequiredRole(userRole, PERMISSIONS.analyticsAccess);
}

export function canAccessPayments(userRole: UserRole | null | undefined): boolean {
  return hasRequiredRole(userRole, PERMISSIONS.paymentAccess);
}

export function canAccessOperations(userRole: UserRole | null | undefined): boolean {
  return hasRequiredRole(userRole, PERMISSIONS.operationsAccess);
}

export function canAccessSupport(userRole: UserRole | null | undefined): boolean {
  return hasRequiredRole(userRole, PERMISSIONS.supportAccess);
}

export function isCustomerUser(userRole: UserRole | null | undefined): boolean {
  return hasRequiredRole(userRole, PERMISSIONS.customerOnly);
}

export function isStaffUser(userRole: UserRole | null | undefined): boolean {
  return hasRequiredRole(userRole, PERMISSIONS.staffOnly);
}

export function canAccessPath(
  pathname: string,
  user: Pick<SessionUser, "role"> | null | undefined,
  isAuthenticated: boolean,
): boolean {
  const userRole = user?.role ?? null;

  if (isPublicRoute(pathname)) {
    return true;
  }

  if (isProtectedRoute(pathname)) {
    return isAuthenticated;
  }

  if (isAdminRoute(pathname)) {
    if (!isAuthenticated) {
      return false;
    }

    const normalized = normalizePathname(pathname);

    if (
      matchesPrefix(normalized, routes.admin.analytics) ||
      matchesPrefix(normalized, routes.admin.analyticsSales) ||
      matchesPrefix(normalized, routes.admin.analyticsRevenue) ||
      matchesPrefix(normalized, routes.admin.analyticsOrders) ||
      matchesPrefix(normalized, routes.admin.analyticsPayments) ||
      matchesPrefix(normalized, routes.admin.analyticsShipping) ||
      matchesPrefix(normalized, routes.admin.analyticsReviews) ||
      matchesPrefix(normalized, routes.admin.analyticsCustomers) ||
      matchesPrefix(normalized, routes.admin.analyticsSnapshots)
    ) {
      return canAccessAnalytics(userRole);
    }

    if (
      matchesPrefix(normalized, routes.admin.payments) ||
      (typeof routes.admin.paymentDetail === "function" &&
        matchesPrefix(normalized, "/admin/payments"))
    ) {
      return canAccessPayments(userRole) || canAccessAdmin(userRole);
    }

    if (
      matchesPrefix(normalized, routes.admin.orders) ||
      matchesPrefix(normalized, routes.admin.shipping)
    ) {
      return canAccessOperations(userRole) || canAccessAdmin(userRole);
    }

    if (
      matchesPrefix(normalized, routes.admin.reviews) ||
      matchesPrefix(normalized, routes.admin.notifications) ||
      matchesPrefix(normalized, routes.admin.users)
    ) {
      return canAccessSupport(userRole) || canAccessAdmin(userRole);
    }

    return canAccessAdmin(userRole);
  }

  return true;
}

export function shouldRedirectAuthenticatedUser(pathname: string): boolean {
  return isAuthScreen(pathname);
}

export function getDefaultProtectedRouteForUser(
  user: Pick<SessionUser, "role"> | null | undefined,
): string {
  const userRole = user?.role ?? null;

  if (!userRole) {
    return routes.public.login;
  }

  if (canAccessAnalytics(userRole)) {
    return routes.admin.analytics;
  }

  if (canAccessAdmin(userRole)) {
    return routes.admin.home;
  }

  return routes.protected.account;
}

export function getUnauthorizedRedirectPath(
  user: Pick<SessionUser, "role"> | null | undefined,
  isAuthenticated: boolean,
): string {
  if (!isAuthenticated) {
    return routes.public.login;
  }

  return getDefaultProtectedRouteForUser(user);
}

export function evaluateRouteAccess(params: {
  pathname: string;
  user: Pick<SessionUser, "role"> | null | undefined;
  isAuthenticated: boolean;
}) {
  const { pathname, user, isAuthenticated } = params;

  const allowed = canAccessPath(pathname, user, isAuthenticated);

  return {
    allowed,
    isPublic: isPublicRoute(pathname),
    isProtected: isProtectedRoute(pathname),
    isAdmin: isAdminRoute(pathname),
    redirectTo: allowed
      ? null
      : getUnauthorizedRedirectPath(user, isAuthenticated),
  };
}