from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ech.products.models import Product
from ech.reviews.constants.messages import (
    REVIEW_NOT_FOUND,
)
from ech.reviews.exceptions import (
    ReviewException,
    ReviewNotFoundException,
)
from ech.reviews.selectors import (
    get_review_by_id,
    list_reviews_for_customer,
    list_reviews_for_management,
    list_public_reviews_by_product,
)
from ech.reviews.filters import ReviewFilter
from ech.reviews.api.pagination import ReviewsPagination
from ech.reviews.api.permissions import (
    CanManageReviews,
    IsReviewOwner,
)
from ech.reviews.api.serializers import (
    CreateReviewSerializer,
    ReviewListSerializer,
    ReviewDetailSerializer,
    ReviewUpdateSerializer,
    ReviewCancelSerializer,
    ReviewModerationSerializer,
    ReviewManagementListSerializer,
    ReviewManagementDetailSerializer,
    ProductPublicReviewSerializer,
    ProductReviewSummarySerializer,
)
from ech.reviews.services.cache_service import ReviewsCacheService


class ReviewCreateAPIView(CreateAPIView):
    """
    API endpoint for creating a new review.
    Restricted to authenticated users.
    """

    serializer_class = CreateReviewSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        try:
            review = serializer.save()
        except ReviewException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = ReviewDetailSerializer(
            review,
            context={"request": request},
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class ReviewListAPIView(ListAPIView):
    """
    API endpoint for listing reviews of the authenticated customer.
    """

    serializer_class = ReviewListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ReviewsPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReviewFilter

    def get_queryset(self):
        return list_reviews_for_customer(customer=self.request.user)

    def list(self, request, *args, **kwargs):
        filters = dict(request.query_params.items())
        customer_id = request.user.id

        def build_response_data():
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data).data

            serializer = self.get_serializer(queryset, many=True)
            return serializer.data

        response_data = ReviewsCacheService.get_or_set_customer_review_list(
            customer_id=customer_id,
            filters=filters,
            callback=build_response_data,
        )

        return Response(response_data, status=status.HTTP_200_OK)


class ReviewDetailAPIView(RetrieveAPIView):
    """
    API endpoint for retrieving a specific customer-owned review detail.
    """

    serializer_class = ReviewDetailSerializer
    permission_classes = [IsAuthenticated, IsReviewOwner]
    lookup_url_kwarg = "review_id"

    def get_object(self):
        review_id = self.kwargs.get(self.lookup_url_kwarg)

        try:
            review = get_review_by_id(review_id=review_id)
        except ReviewNotFoundException:
            raise NotFound(REVIEW_NOT_FOUND)

        self.check_object_permissions(self.request, review)
        return review

    def retrieve(self, request, *args, **kwargs):
        review = self.get_object()

        def build_response_data():
            serializer = self.get_serializer(
                review,
                context={"request": request},
            )
            return serializer.data

        response_data = ReviewsCacheService.get_or_set_review_detail(
            review_id=review.id,
            callback=build_response_data,
        )

        return Response(response_data, status=status.HTTP_200_OK)


class ReviewUpdateAPIView(APIView):
    """
    API endpoint for updating customer-editable review fields.
    """

    permission_classes = [IsAuthenticated, IsReviewOwner]

    def patch(self, request, review_id, *args, **kwargs):
        try:
            review = get_review_by_id(review_id=review_id)
        except ReviewNotFoundException:
            raise NotFound(REVIEW_NOT_FOUND)

        self.check_object_permissions(request, review)

        serializer = ReviewUpdateSerializer(
            data=request.data,
            context={
                "request": request,
                "review": review,
            },
        )
        serializer.is_valid(raise_exception=True)

        try:
            updated_review = serializer.save(
                review=review,
                performed_by=request.user,
            )
        except ReviewException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = ReviewDetailSerializer(
            updated_review,
            context={"request": request},
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


class ReviewCancelAPIView(APIView):
    """
    API endpoint for cancelling a customer-owned review.
    """

    permission_classes = [IsAuthenticated, IsReviewOwner]

    def post(self, request, review_id, *args, **kwargs):
        try:
            review = get_review_by_id(review_id=review_id)
        except ReviewNotFoundException:
            raise NotFound(REVIEW_NOT_FOUND)

        self.check_object_permissions(request, review)

        serializer = ReviewCancelSerializer(
            data=request.data,
            context={
                "request": request,
                "review": review,
            },
        )
        serializer.is_valid(raise_exception=True)

        try:
            updated_review = serializer.save(
                review=review,
                performed_by=request.user,
            )
        except ReviewException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = ReviewDetailSerializer(
            updated_review,
            context={"request": request},
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


class ReviewModerationAPIView(APIView):
    """
    API endpoint for performing moderation actions on reviews.
    Restricted to review management roles.
    """

    permission_classes = [IsAuthenticated, CanManageReviews]

    def post(self, request, review_id, *args, **kwargs):
        try:
            review = get_review_by_id(review_id=review_id)
        except ReviewNotFoundException:
            raise NotFound(REVIEW_NOT_FOUND)

        serializer = ReviewModerationSerializer(
            data=request.data,
            context={
                "request": request,
                "review": review,
            },
        )
        serializer.is_valid(raise_exception=True)

        try:
            updated_review = serializer.save(
                review=review,
                performed_by=request.user,
            )
        except ReviewException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = ReviewManagementDetailSerializer(
            updated_review,
            context={"request": request},
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


class ProductPublicReviewListAPIView(ListAPIView):
    """
    Public API endpoint for listing approved reviews of a specific product.
    """

    serializer_class = ProductPublicReviewSerializer
    pagination_class = ReviewsPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReviewFilter

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")
        product = get_object_or_404(Product, id=product_id)
        return list_public_reviews_by_product(product=product)

    def list(self, request, *args, **kwargs):
        product_id = self.kwargs.get("product_id")
        get_object_or_404(Product, id=product_id)

        filters = dict(request.query_params.items())

        def build_response_data():
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data).data

            serializer = self.get_serializer(queryset, many=True)
            return serializer.data

        response_data = ReviewsCacheService.get_or_set_public_product_review_list(
            product_id=product_id,
            filters=filters,
            callback=build_response_data,
        )

        return Response(response_data, status=status.HTTP_200_OK)


class ProductReviewSummaryAPIView(APIView):
    """
    Public API endpoint for retrieving aggregated review summary for a product.
    """

    def get(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id=product_id)

        def build_response_data():
            summary_data = ProductReviewSummarySerializer.build_summary(product)
            serializer = ProductReviewSummarySerializer(summary_data)
            return serializer.data

        response_data = ReviewsCacheService.get_or_set_product_review_summary(
            product_id=product_id,
            callback=build_response_data,
        )

        return Response(response_data, status=status.HTTP_200_OK)


class ReviewManagementListAPIView(ListAPIView):
    """
    API endpoint for staff review management listing.
    """

    serializer_class = ReviewManagementListSerializer
    permission_classes = [IsAuthenticated, CanManageReviews]
    pagination_class = ReviewsPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReviewFilter

    def get_queryset(self):
        return list_reviews_for_management()

    def list(self, request, *args, **kwargs):
        filters = dict(request.query_params.items())

        def build_response_data():
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data).data

            serializer = self.get_serializer(queryset, many=True)
            return serializer.data

        response_data = ReviewsCacheService.get_or_set_management_review_list(
            filters=filters,
            callback=build_response_data,
        )

        return Response(response_data, status=status.HTTP_200_OK)


class ReviewManagementDetailAPIView(RetrieveAPIView):
    """
    API endpoint for staff review management detail.
    """

    serializer_class = ReviewManagementDetailSerializer
    permission_classes = [IsAuthenticated, CanManageReviews]
    lookup_url_kwarg = "review_id"

    def get_object(self):
        review_id = self.kwargs.get(self.lookup_url_kwarg)

        try:
            review = get_review_by_id(review_id=review_id)
        except ReviewNotFoundException:
            raise NotFound(REVIEW_NOT_FOUND)

        return review

    def retrieve(self, request, *args, **kwargs):
        review = self.get_object()

        def build_response_data():
            serializer = self.get_serializer(
                review,
                context={"request": request},
            )
            return serializer.data

        response_data = ReviewsCacheService.get_or_set_review_detail(
            review_id=review.id,
            callback=build_response_data,
        )

        return Response(response_data, status=status.HTTP_200_OK)