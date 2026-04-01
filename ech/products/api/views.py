from django.conf import settings
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import (
    OrderingFilter,
    SearchFilter,
)
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ech.products.api.pagination import DefaultPagination
from ech.products.api.permissions import (
    IsOperationsAdminOrSuperAdmin,
    IsProductOwnerOrManager,
    IsPublicOrProductManager,
)
from ech.products.api.serializers import (
    ProductCreateSerializer,
    ProductDetailSerializer,
    ProductImageUploadSerializer,
    ProductListSerializer,
    ProductUpdateSerializer,
)
from ech.products.filters import ProductFilter
from ech.products.models import Product
from ech.products.services.product_delete_service import delete_product
from ech.products.utils.cache_keys import (
    build_product_list_cache_key,
    get_product_from_cache,
    get_product_list_cache,
    set_product_cache,
    set_product_list_cache,
)


class ProductCreateAPIView(APIView):
    """
    Creates a new product.
    Only operations staff, admin and superadmin can perform this action.
    """

    permission_classes = [IsOperationsAdminOrSuperAdmin]

    def post(self, request):
        serializer = ProductCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "idempotency_key": request.headers.get("Idempotency-Key"),
            },
        )
        serializer.is_valid(raise_exception=True)

        product = serializer.save()

        output_serializer = ProductDetailSerializer(product)

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class ProductListAPIView(ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = ProductFilter

    search_fields = [
        "name",
        "brand",
        "description",
    ]

    ordering_fields = [
        "price",
        "created_at",
        "name",
    ]

    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            Product.objects
            .filter(is_active=True)
            .select_related("sold_by")
            .prefetch_related("images")
        )

    def get(self, request, *args, **kwargs):
        if getattr(settings, "RUNNING_TESTS", False):
            return self.list(request, *args, **kwargs)

        cache_key = build_product_list_cache_key(request)
        cached_response = get_product_list_cache(cache_key)

        if cached_response is not None:
            return Response(cached_response)

        response = self.list(request, *args, **kwargs)
        set_product_list_cache(cache_key, response.data)

        return response


class ProductDetailAPIView(APIView):
    """
    Returns product details.
    """

    permission_classes = [IsPublicOrProductManager]

    def get(self, request, product_id):
        product = get_product_from_cache(product_id)

        if not product:
            product = get_object_or_404(
                Product.objects
                .filter(is_active=True)
                .select_related("inventory_record", "sold_by")
                .prefetch_related("images"),
                id=product_id,
            )
            set_product_cache(product)

        serializer = ProductDetailSerializer(product)

        return Response(serializer.data)


class ProductImageUploadAPIView(APIView):
    """
    Upload images for a product.
    """

    permission_classes = [IsProductOwnerOrManager]

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        self.check_object_permissions(request, product)

        serializer = ProductImageUploadSerializer(
            data=request.data,
            context={
                "product": product,
                "request": request,
            },
        )
        serializer.is_valid(raise_exception=True)

        image = serializer.save()

        return Response(
            {
                "id": image.id,
                "image": image.image.url,
                "order": image.order,
            },
            status=status.HTTP_201_CREATED,
        )


class ProductUpdateAPIView(APIView):
    """
    Updates a product.
    """

    permission_classes = [IsProductOwnerOrManager]

    def patch(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        self.check_object_permissions(request, product)

        serializer = ProductUpdateSerializer(
            product,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        product = serializer.save()

        output_serializer = ProductDetailSerializer(product)

        return Response(output_serializer.data)


class ProductDeleteAPIView(APIView):
    """
    Soft delete a product.
    """

    permission_classes = [IsProductOwnerOrManager]

    def delete(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        self.check_object_permissions(request, product)

        delete_product(
            product_id=product.id,
            performed_by=request.user,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)