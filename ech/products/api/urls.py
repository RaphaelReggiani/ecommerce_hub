from django.urls import path

from ech.products.api.views import (
    ProductCreateAPIView,
    ProductListAPIView,
    ProductDetailAPIView,
    ProductImageUploadAPIView,
    ProductUpdateAPIView,
    ProductDeleteAPIView,
)

app_name = "products-api"

urlpatterns = [

    path("", ProductCreateAPIView.as_view(),name="product-create"),

    path("list/", ProductListAPIView.as_view(), name="product-list"),

    path("<uuid:product_id>/", ProductDetailAPIView.as_view(), name="product-detail"),

    path("<uuid:product_id>/images/", ProductImageUploadAPIView.as_view(),name="product-image-upload"),

    path("<uuid:product_id>/update/", ProductUpdateAPIView.as_view(), name="product-update"),

    path("<uuid:product_id>/delete/", ProductDeleteAPIView.as_view(), name="product-delete"),
]