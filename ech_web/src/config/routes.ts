export const routes = {
  public: {
    home: "/",
    login: "/login",
    register: "/register",
    forgotPassword: "/forgot-password",
    resetPassword: "/reset-password",
    products: "/products",
    productDetail: (slug: string) => `/products/${slug}`,
  },

  protected: {
    cart: "/cart",
    checkout: "/checkout",
    account: "/account",
    profile: "/account/profile",
    orders: "/account/orders",
    orderDetail: (id: string | number) => `/account/orders/${id}`,
    payments: "/account/payments",
    paymentDetail: (id: string | number) => `/account/payments/${id}`,
    shipping: "/account/shipping",
    shipmentDetail: (id: string | number) => `/account/shipping/${id}`,
    notifications: "/account/notifications",
    reviews: "/account/reviews",
  },

  admin: {
    home: "/admin",
    users: "/admin/users",
    products: "/admin/products",
    createProduct: "/admin/products/create",
    editProduct: (id: string | number) => `/admin/products/${id}/edit`,
    orders: "/admin/orders",
    orderDetail: (id: string | number) => `/admin/orders/${id}`,
    payments: "/admin/payments",
    paymentDetail: (id: string | number) => `/admin/payments/${id}`,
    shipping: "/admin/shipping",
    shipmentDetail: (id: string | number) => `/admin/shipping/${id}`,
    reviews: "/admin/reviews",
    notifications: "/admin/notifications",
    analytics: "/admin/analytics",
    analyticsSales: "/admin/analytics/sales",
    analyticsRevenue: "/admin/analytics/revenue",
    analyticsOrders: "/admin/analytics/orders",
    analyticsPayments: "/admin/analytics/payments",
    analyticsShipping: "/admin/analytics/shipping",
    analyticsReviews: "/admin/analytics/reviews",
    analyticsCustomers: "/admin/analytics/customers",
    analyticsSnapshots: "/admin/analytics/snapshots",
  },
} as const;

export const publicRoutePrefixes = [
  routes.public.home,
  routes.public.login,
  routes.public.register,
  routes.public.forgotPassword,
  routes.public.resetPassword,
  routes.public.products,
] as const;

export const protectedRoutePrefixes = [
  "/cart",
  "/checkout",
  "/account",
] as const;

export const adminRoutePrefixes = [
  "/admin",
] as const;