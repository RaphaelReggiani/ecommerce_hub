from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ech.products.models import Product

from ech.products.api.serializers import (
    ProductCreateSerializer,
    ProductImageUploadSerializer,
    ProductDetailSerializer,
)

from ech.products.api.permissions import (
    IsOperationsAdminOrSuperAdmin,
    IsPublicOrProductManager,
    IsProductOwnerOrManager,
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


class ProductListAPIView(APIView):
    """
    Public product catalog endpoint.
    """

    permission_classes = [IsPublicOrProductManager]

    def get(self, request):

        products = (
            Product.objects
            .filter(is_active=True)
            .select_related("inventory_record")
            .prefetch_related("images")
            .order_by("-created_at")
        )

        serializer = ProductDetailSerializer(
            products,
            many=True
        )

        return Response(serializer.data)


class ProductDetailAPIView(APIView):
    """
    Returns product details.
    """

    permission_classes = [IsPublicOrProductManager]

    def get(self, request, product_id):

        product = get_object_or_404(
            Product.objects
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