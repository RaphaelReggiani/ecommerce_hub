from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ech.products.models import Product
from ech.products.api.serializers import ProductListSerializer
from ech.products.api.pagination import DefaultPagination
from ech.products.filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import (
    SearchFilter, 
    OrderingFilter,
)

from ech.products.api.serializers import (
    ProductCreateSerializer,
    ProductImageUploadSerializer,
    ProductDetailSerializer,
    ProductUpdateSerializer,
)

from ech.products.api.permissions import (
    IsOperationsAdminOrSuperAdmin,
    IsPublicOrProductManager,
    IsProductOwnerOrManager,
)

from ech.products.services.product_delete_service import (
    delete_product,
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
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        product = serializer.save()

        output_serializer = ProductDetailSerializer(product)

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED
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


class ProductDetailAPIView(APIView):
    """
    Returns product details.
    """

    permission_classes = [IsPublicOrProductManager]

    def get(self, request, product_id):

        product = get_object_or_404(
            Product.objects
            .filter(is_active=True)
            .select_related("inventory_record")
            .prefetch_related("images"),
            id=product_id,
        )

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
            context={"product": product},
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

        delete_product(product_id=product.id)

        return Response(status=status.HTTP_204_NO_CONTENT)