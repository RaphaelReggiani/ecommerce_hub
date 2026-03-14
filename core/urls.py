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
    path("api/v1/products/", include("ech.products.api.urls")),
    path("api/v1/orders/", include("ech.orders.api.urls")),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)