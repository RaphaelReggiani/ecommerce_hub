from django.urls import path

from ech.products.api.views import (
    ProductCreateAPIView,
    ProductListAPIView,
    ProductDetailAPIView,
    ProductImageUploadAPIView,
    ProductUpdateAPIView,
    ProductDeleteAPIView,
)

urlpatterns = [
    # Create product
    path("", ProductCreateAPIView.as_view(),name="product-create"),

    # List products
    path("list/", ProductListAPIView.as_view(), name="product-list"),

    # Product detail
    path("<uuid:product_id>/", ProductDetailAPIView.as_view(), name="product-detail"),

    # Upload product images
    path("<uuid:product_id>/images/", ProductImageUploadAPIView.as_view(),name="product-image-upload"),

    # Update product
    path("<uuid:product_id>/update/", ProductUpdateAPIView.as_view(), name="product-update"),

    # Delete product
    path("<uuid:product_id>/delete/", ProductDeleteAPIView.as_view(), name="product-delete"),
]