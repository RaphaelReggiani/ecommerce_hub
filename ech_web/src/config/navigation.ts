import { PERMISSIONS } from "@/config/permissions";
import { routes } from "@/config/routes";

export type NavigationItem = {
  label: string;
  href: string;
  exact?: boolean;
  requiredRoles?: readonly string[];
  children?: readonly NavigationItem[];
};

export const publicNavigation = [
  {
    label: "Home",
    href: routes.public.home,
    exact: true,
  },
  {
    label: "Products",
    href: routes.public.products,
  },
  {
    label: "Login",
    href: routes.public.login,
    exact: true,
  },
  {
    label: "Register",
    href: routes.public.register,
    exact: true,
  },
] as const satisfies readonly NavigationItem[];

export const accountNavigation = [
  {
    label: "Profile",
    href: routes.protected.profile,
    exact: true,
  },
  {
    label: "Orders",
    href: routes.protected.orders,
  },
  {
    label: "Payments",
    href: routes.protected.payments,
  },
  {
    label: "Shipping",
    href: routes.protected.shipping,
  },
  {
    label: "Notifications",
    href: routes.protected.notifications,
    exact: true,
  },
  {
    label: "Reviews",
    href: routes.protected.reviews,
    exact: true,
  },
] as const satisfies readonly NavigationItem[];

export const cartNavigation = [
  {
    label: "Cart",
    href: routes.protected.cart,
    exact: true,
  },
  {
    label: "Checkout",
    href: routes.protected.checkout,
    exact: true,
  },
] as const satisfies readonly NavigationItem[];

export const adminNavigation = [
  {
    label: "Dashboard",
    href: routes.admin.home,
    exact: true,
    requiredRoles: PERMISSIONS.adminAccess,
  },
  {
    label: "Users",
    href: routes.admin.users,
    exact: true,
    requiredRoles: PERMISSIONS.supportAccess,
  },
  {
    label: "Products",
    href: routes.admin.products,
    requiredRoles: PERMISSIONS.adminAccess,
  },
  {
    label: "Orders",
    href: routes.admin.orders,
    requiredRoles: PERMISSIONS.operationsAccess,
  },
  {
    label: "Payments",
    href: routes.admin.payments,
    requiredRoles: PERMISSIONS.paymentAccess,
  },
  {
    label: "Shipping",
    href: routes.admin.shipping,
    requiredRoles: PERMISSIONS.operationsAccess,
  },
  {
    label: "Reviews",
    href: routes.admin.reviews,
    exact: true,
    requiredRoles: PERMISSIONS.supportAccess,
  },
  {
    label: "Notifications",
    href: routes.admin.notifications,
    exact: true,
    requiredRoles: PERMISSIONS.supportAccess,
  },
  {
    label: "Analytics",
    href: routes.admin.analytics,
    requiredRoles: PERMISSIONS.analyticsAccess,
    children: [
      {
        label: "Overview",
        href: routes.admin.analytics,
        exact: true,
        requiredRoles: PERMISSIONS.analyticsAccess,
      },
      {
        label: "Sales",
        href: routes.admin.analyticsSales,
        exact: true,
        requiredRoles: PERMISSIONS.analyticsAccess,
      },
      {
        label: "Orders",
        href: routes.admin.analyticsOrders,
        exact: true,
        requiredRoles: PERMISSIONS.analyticsAccess,
      },
      {
        label: "Payments",
        href: routes.admin.analyticsPayments,
        exact: true,
        requiredRoles: PERMISSIONS.analyticsAccess,
      },
      {
        label: "Shipping",
        href: routes.admin.analyticsShipping,
        exact: true,
        requiredRoles: PERMISSIONS.analyticsAccess,
      },
      {
        label: "Reviews",
        href: routes.admin.analyticsReviews,
        exact: true,
        requiredRoles: PERMISSIONS.analyticsAccess,
      },
      {
        label: "Customers",
        href: routes.admin.analyticsCustomers,
        exact: true,
        requiredRoles: PERMISSIONS.analyticsAccess,
      },
      {
        label: "Snapshots",
        href: routes.admin.analyticsSnapshots,
        exact: true,
        requiredRoles: PERMISSIONS.analyticsAccess,
      },
    ],
  },
] as const satisfies readonly NavigationItem[];

export const headerNavigation = {
  public: publicNavigation,
  authenticated: [...accountNavigation, ...cartNavigation] as const,
  admin: adminNavigation,
} as const;

export const sidebarNavigation = {
  account: accountNavigation,
  admin: adminNavigation,
} as const;

export const userMenuNavigation = [
  {
    label: "My profile",
    href: routes.protected.profile,
    exact: true,
  },
  {
    label: "My orders",
    href: routes.protected.orders,
  },
  {
    label: "My payments",
    href: routes.protected.payments,
  },
  {
    label: "My shipping",
    href: routes.protected.shipping,
  },
] as const satisfies readonly NavigationItem[];