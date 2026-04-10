from django.utils.dateparse import parse_datetime

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ech.analytics.api.pagination import AnalyticsPagination
from ech.analytics.api.permissions import (
    CanAccessAnalytics,
    CanAccessAnalyticsObject,
)
from ech.analytics.api.serializers import (
    AnalyticsCustomerSummarySerializer,
    AnalyticsDashboardSummarySerializer,
    AnalyticsOrderFunnelSerializer,
    AnalyticsPaymentOverviewSerializer,
    AnalyticsProductPerformanceSerializer,
    AnalyticsReviewOverviewSerializer,
    AnalyticsSalesOverviewSerializer,
    AnalyticsShippingOverviewSerializer,
    AnalyticsSnapshotDetailSerializer,
    AnalyticsSnapshotListSerializer,
    AnalyticsSnapshotRefreshSerializer,
    AnalyticsUserOverviewSerializer,
)
from ech.analytics.constants.messages import (
    ANALYTICS_SNAPSHOT_NOT_FOUND,
)
from ech.analytics.exceptions import (
    AnalyticsCustomerUnavailableException,
    AnalyticsDashboardUnavailableException,
    AnalyticsOrderUnavailableException,
    AnalyticsPaymentUnavailableException,
    AnalyticsProductUnavailableException,
    AnalyticsReviewUnavailableException,
    AnalyticsSalesUnavailableException,
    AnalyticsShippingUnavailableException,
    AnalyticsSnapshotNotFoundException,
    AnalyticsSnapshotRefreshException,
    AnalyticsUserUnavailableException,
)
from ech.analytics.filters import (
    AnalyticsSnapshotManagementFilter,
)
from ech.analytics.selectors import (
    get_analytics_snapshot_by_id,
    list_analytics_snapshots,
)
from ech.analytics.services.analytic_customer_summary_service import (
    AnalyticsCustomerSummaryService,
)
from ech.analytics.services.analytic_dashboard_summary_service import (
    AnalyticsDashboardSummaryService,
)
from ech.analytics.services.analytic_order_funnel_service import (
    AnalyticsOrderFunnelService,
)
from ech.analytics.services.analytic_payment_overview_service import (
    AnalyticsPaymentOverviewService,
)
from ech.analytics.services.analytic_product_performance_service import (
    AnalyticsProductPerformanceService,
)
from ech.analytics.services.analytic_review_overview_service import (
    AnalyticsReviewOverviewService,
)
from ech.analytics.services.analytic_sales_overview_service import (
    AnalyticsSalesOverviewService,
)
from ech.analytics.services.analytic_shipping_overview_service import (
    AnalyticsShippingOverviewService,
)
from ech.analytics.services.analytic_user_overview_service import (
    AnalyticsUserOverviewService,
)


class AnalyticsBasePeriodAPIView(APIView):
    """
    Base API view for analytics endpoints that accept period-based query params.
    """

    permission_classes = [IsAuthenticated, CanAccessAnalytics]

    @staticmethod
    def _parse_period_params(request):
        """
        Parse analytics period query params from request.
        """

        period_type = request.query_params.get("period_type")
        period_start = request.query_params.get("period_start")
        period_end = request.query_params.get("period_end")

        resolved_period_start = None
        resolved_period_end = None

        if period_start:
            resolved_period_start = parse_datetime(period_start)
            if resolved_period_start is None:
                raise ValidationError(
                    {"period_start": "Invalid datetime format."}
                )

        if period_end:
            resolved_period_end = parse_datetime(period_end)
            if resolved_period_end is None:
                raise ValidationError(
                    {"period_end": "Invalid datetime format."}
                )

        if not period_type:
            raise ValidationError(
                {"period_type": "This query parameter is required."}
            )

        return period_type, resolved_period_start, resolved_period_end


class AnalyticsDashboardSummaryAPIView(AnalyticsBasePeriodAPIView):
    """
    API endpoint for retrieving analytics dashboard summary data.
    """

    def get(self, request, *args, **kwargs):
        period_type, period_start, period_end = self._parse_period_params(
            request
        )

        try:
            payload = AnalyticsDashboardSummaryService.get_summary(
                period_type=period_type,
                period_start=period_start,
                period_end=period_end,
                performed_by=request.user,
            )
        except AnalyticsDashboardUnavailableException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AnalyticsDashboardSummarySerializer(
            payload,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnalyticsSalesOverviewAPIView(AnalyticsBasePeriodAPIView):
    """
    API endpoint for retrieving sales analytics overview data.
    """

    def get(self, request, *args, **kwargs):
        period_type, period_start, period_end = self._parse_period_params(
            request
        )

        try:
            payload = AnalyticsSalesOverviewService.get_overview(
                period_type=period_type,
                period_start=period_start,
                period_end=period_end,
                performed_by=request.user,
            )
        except AnalyticsSalesUnavailableException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AnalyticsSalesOverviewSerializer(
            payload,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnalyticsOrderFunnelAPIView(AnalyticsBasePeriodAPIView):
    """
    API endpoint for retrieving order funnel analytics data.
    """

    def get(self, request, *args, **kwargs):
        period_type, period_start, period_end = self._parse_period_params(
            request
        )

        try:
            payload = AnalyticsOrderFunnelService.get_funnel(
                period_type=period_type,
                period_start=period_start,
                period_end=period_end,
                performed_by=request.user,
            )
        except AnalyticsOrderUnavailableException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AnalyticsOrderFunnelSerializer(
            payload,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnalyticsPaymentOverviewAPIView(AnalyticsBasePeriodAPIView):
    """
    API endpoint for retrieving payment analytics overview data.
    """

    def get(self, request, *args, **kwargs):
        period_type, period_start, period_end = self._parse_period_params(
            request
        )

        try:
            payload = AnalyticsPaymentOverviewService.get_overview(
                period_type=period_type,
                period_start=period_start,
                period_end=period_end,
                performed_by=request.user,
            )
        except AnalyticsPaymentUnavailableException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AnalyticsPaymentOverviewSerializer(
            payload,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnalyticsShippingOverviewAPIView(AnalyticsBasePeriodAPIView):
    """
    API endpoint for retrieving shipping analytics overview data.
    """

    def get(self, request, *args, **kwargs):
        period_type, period_start, period_end = self._parse_period_params(
            request
        )

        try:
            payload = AnalyticsShippingOverviewService.get_overview(
                period_type=period_type,
                period_start=period_start,
                period_end=period_end,
                performed_by=request.user,
            )
        except AnalyticsShippingUnavailableException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AnalyticsShippingOverviewSerializer(
            payload,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnalyticsProductPerformanceAPIView(AnalyticsBasePeriodAPIView):
    """
    API endpoint for retrieving product performance analytics data.
    """

    def get(self, request, *args, **kwargs):
        period_type, period_start, period_end = self._parse_period_params(
            request
        )

        try:
            payload = AnalyticsProductPerformanceService.get_performance(
                period_type=period_type,
                period_start=period_start,
                period_end=period_end,
                performed_by=request.user,
            )
        except AnalyticsProductUnavailableException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AnalyticsProductPerformanceSerializer(
            payload,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnalyticsCustomerSummaryAPIView(AnalyticsBasePeriodAPIView):
    """
    API endpoint for retrieving customer analytics summary data.
    """

    def get(self, request, *args, **kwargs):
        period_type, period_start, period_end = self._parse_period_params(
            request
        )

        try:
            payload = AnalyticsCustomerSummaryService.get_summary(
                period_type=period_type,
                period_start=period_start,
                period_end=period_end,
                performed_by=request.user,
            )
        except AnalyticsCustomerUnavailableException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AnalyticsCustomerSummarySerializer(
            payload,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnalyticsUserOverviewAPIView(AnalyticsBasePeriodAPIView):
    """
    API endpoint for retrieving user analytics overview data.
    """

    def get(self, request, *args, **kwargs):
        period_type, period_start, period_end = self._parse_period_params(
            request
        )

        try:
            payload = AnalyticsUserOverviewService.get_overview(
                period_type=period_type,
                period_start=period_start,
                period_end=period_end,
                performed_by=request.user,
            )
        except AnalyticsUserUnavailableException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AnalyticsUserOverviewSerializer(
            payload,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnalyticsReviewOverviewAPIView(AnalyticsBasePeriodAPIView):
    """
    API endpoint for retrieving review analytics overview data.
    """

    def get(self, request, *args, **kwargs):
        period_type, period_start, period_end = self._parse_period_params(
            request
        )

        try:
            payload = AnalyticsReviewOverviewService.get_overview(
                period_type=period_type,
                period_start=period_start,
                period_end=period_end,
                performed_by=request.user,
            )
        except AnalyticsReviewUnavailableException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AnalyticsReviewOverviewSerializer(
            payload,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnalyticsSnapshotListAPIView(ListAPIView):
    """
    API endpoint for analytics snapshot management listing.
    """

    serializer_class = AnalyticsSnapshotListSerializer
    permission_classes = [IsAuthenticated, CanAccessAnalytics]
    pagination_class = AnalyticsPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = AnalyticsSnapshotManagementFilter

    def get_queryset(self):
        return list_analytics_snapshots()


class AnalyticsSnapshotDetailAPIView(RetrieveAPIView):
    """
    API endpoint for analytics snapshot detail retrieval.
    """

    serializer_class = AnalyticsSnapshotDetailSerializer
    permission_classes = [IsAuthenticated, CanAccessAnalyticsObject]
    lookup_url_kwarg = "snapshot_id"

    def get_object(self):
        snapshot_id = self.kwargs.get(self.lookup_url_kwarg)

        try:
            snapshot = get_analytics_snapshot_by_id(snapshot_id=snapshot_id)
        except AnalyticsSnapshotNotFoundException:
            raise NotFound(ANALYTICS_SNAPSHOT_NOT_FOUND)

        self.check_object_permissions(self.request, snapshot)
        return snapshot


class AnalyticsSnapshotRefreshAPIView(APIView):
    """
    API endpoint for refreshing an analytics snapshot.
    """

    permission_classes = [IsAuthenticated, CanAccessAnalytics]

    def post(self, request, snapshot_id, *args, **kwargs):
        try:
            snapshot = get_analytics_snapshot_by_id(snapshot_id=snapshot_id)
        except AnalyticsSnapshotNotFoundException:
            raise NotFound(ANALYTICS_SNAPSHOT_NOT_FOUND)

        serializer = AnalyticsSnapshotRefreshSerializer(
            data=request.data,
            context={
                "request": request,
                "snapshot": snapshot,
            },
        )
        serializer.is_valid(raise_exception=True)

        try:
            refreshed_snapshot = serializer.save(
                snapshot=snapshot,
                performed_by=request.user,
            )
        except AnalyticsSnapshotRefreshException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = AnalyticsSnapshotDetailSerializer(
            refreshed_snapshot,
            context={"request": request},
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )