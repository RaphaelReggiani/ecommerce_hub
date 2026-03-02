from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("ech.urls")),
    path("users/", include("ech.users.urls", namespace="users")),
    # path("products/", include("ech.products.urls")),
    # path("payment/", include("ech.payment.urls")),
    # path("delivery/", include("ech.delivery.urls")),
    # path("api/", include("api.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)