from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [

    # =========================
    # ADMIN
    # =========================

    path("admin/", admin.site.urls),

    # =========================
    # WEB
    # =========================

    path("", include("ech_web.urls")),
    # path("users/", include("ech_web.users.config.urls", namespace="users")),
    # path("products/", include("ech.products.urls")),
    # path("payment/", include("ech.payment.urls")),
    # path("delivery/", include("ech.delivery.urls")),

    # =========================
    # API
    # =========================

    path("api/v1/users/", include(("ech.users.api.urls", "users-api"), namespace="users-api")),

    path("api/v1/products/", include(("ech.products.api.urls", "products-api"), namespace="products-api")),

    path("api/v1/orders/", include(("ech.orders.api.urls", "orders-api"), namespace="orders-api")),

    path("api/v1/payments/", include(("ech.payments.api.urls", "payments-api"), namespace="payments-api")),
    
    path("api/v1/shipping/", include(("ech.shipping.api.urls", "shipping-api"), namespace="shipping-api")),

    path("api/v1/reviews/", include(("ech.reviews.api.urls", "reviews-api"), namespace="reviews-api")),

    path("api/v1/notifications/", include(("ech.notifications.api.urls", "notifications-api"), namespace="notifications-api")),

    path("api/v1/analytics/", include(("ech.analytics.api.urls", "analytics-api"), namespace="analytics-api")),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)