from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ech.admin_dashboard.api.pagination import AdminDashboardPagination
from ech.admin_dashboard.api.permissions import (
    CanAccessAdminDashboard,
    CanAccessAdminDashboardObject,
    CanExecuteOrderBulkActions,
    CanModerateReviews,
    CanRetryNotifications,
)
from ech.admin_dashboard.api.serializers import (
    AdminDashboardAlertsSerializer,
    AdminDashboardBulkNotificationRetryResponseSerializer,
    AdminDashboardBulkNotificationRetrySerializer,
    AdminDashboardBulkOrderActionResponseSerializer,
    AdminDashboardBulkOrderActionSerializer,
    AdminDashboardBulkReviewModerationResponseSerializer,
    AdminDashboardBulkReviewModerationSerializer,
    AdminDashboardEventSerializer,
    AdminDashboardLogDetailSerializer,
    AdminDashboardLogListSerializer,
    AdminDashboardOperationalMetricsSerializer,
    AdminDashboardRecentActivitySerializer,
    AdminDashboardSummarySerializer,
)
from ech.admin_dashboard.exceptions import (
    AdminDashboardBulkOrderActionException,
    AdminDashboardNotificationRetryException,
    AdminDashboardOperationalAlertsUnavailableException,
    AdminDashboardOperationalMetricsUnavailableException,
    AdminDashboardRecentActivityUnavailableException,
    AdminDashboardReviewBulkModerationException,
    AdminDashboardSummaryUnavailableException,
)
from ech.admin_dashboard.filters import (
    AdminDashboardEventFilter,
    AdminDashboardLogFilter,
)
from ech.admin_dashboard.models import (
    AdminDashboardEvent,
    AdminDashboardLog,
)
from ech.admin_dashboard.services.admin_dashboard_alerts_service import (
    AdminDashboardAlertsService,
)
from ech.admin_dashboard.services.admin_dashboard_operational_metrics_service import (
    AdminDashboardOperationalMetricsService,
)
from ech.admin_dashboard.services.admin_dashboard_recent_activity_service import (
    AdminDashboardRecentActivityService,
)
from ech.admin_dashboard.services.admin_dashboard_summary_service import (
    AdminDashboardSummaryService,
)


class AdminDashboardSummaryAPIView(APIView):
    """
    API endpoint for retrieving admin dashboard summary metrics.
    """

    permission_classes = [IsAuthenticated, CanAccessAdminDashboard]

    def get(self, request, *args, **kwargs):
        try:
            payload = AdminDashboardSummaryService.get_summary(
                performed_by=request.user,
            )
        except AdminDashboardSummaryUnavailableException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AdminDashboardSummarySerializer(
            payload,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminDashboardOperationalMetricsAPIView(APIView):
    """
    API endpoint for retrieving admin dashboard operational metrics.
    """

    permission_classes = [IsAuthenticated, CanAccessAdminDashboard]

    def get(self, request, *args, **kwargs):
        try:
            payload = AdminDashboardOperationalMetricsService.get_operational_metrics(
                performed_by=request.user,
            )
        except AdminDashboardOperationalMetricsUnavailableException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AdminDashboardOperationalMetricsSerializer(
            payload,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminDashboardRecentActivityAPIView(APIView):
    """
    API endpoint for retrieving recent admin dashboard activity.
    """

    permission_classes = [IsAuthenticated, CanAccessAdminDashboard]

    def get(self, request, *args, **kwargs):
        limit = request.query_params.get("limit")

        if limit is not None:
            try:
                limit = int(limit)
            except (TypeError, ValueError):
                return Response(
                    {"limit": ["A valid integer is required."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if limit <= 0:
                return Response(
                    {"limit": ["Ensure this value is greater than 0."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            payload = AdminDashboardRecentActivityService.get_recent_activity(
                limit=limit,
                performed_by=request.user,
            )
        except AdminDashboardRecentActivityUnavailableException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AdminDashboardRecentActivitySerializer(
            payload,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminDashboardAlertsAPIView(APIView):
    """
    API endpoint for retrieving operational alerts from the admin dashboard.
    """

    permission_classes = [IsAuthenticated, CanAccessAdminDashboard]

    def get(self, request, *args, **kwargs):
        try:
            payload = AdminDashboardAlertsService.get_alerts(
                performed_by=request.user,
            )
        except AdminDashboardOperationalAlertsUnavailableException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AdminDashboardAlertsSerializer(
            payload,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminDashboardBulkOrderActionAPIView(APIView):
    """
    API endpoint for executing bulk administrative actions on orders.
    """

    permission_classes = [IsAuthenticated, CanExecuteOrderBulkActions]

    def post(self, request, *args, **kwargs):
        serializer = AdminDashboardBulkOrderActionSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        try:
            result = serializer.save(
                performed_by=request.user,
            )
        except AdminDashboardBulkOrderActionException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = AdminDashboardBulkOrderActionResponseSerializer(
            result,
            context={"request": request},
        )
        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


class AdminDashboardBulkReviewModerationAPIView(APIView):
    """
    API endpoint for executing bulk review moderation actions.
    """

    permission_classes = [IsAuthenticated, CanModerateReviews]

    def post(self, request, *args, **kwargs):
        serializer = AdminDashboardBulkReviewModerationSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        try:
            result = serializer.save(
                performed_by=request.user,
            )
        except AdminDashboardReviewBulkModerationException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = AdminDashboardBulkReviewModerationResponseSerializer(
            result,
            context={"request": request},
        )
        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


class AdminDashboardBulkNotificationRetryAPIView(APIView):
    """
    API endpoint for retrying failed notifications in bulk.
    """

    permission_classes = [IsAuthenticated, CanRetryNotifications]

    def post(self, request, *args, **kwargs):
        serializer = AdminDashboardBulkNotificationRetrySerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        try:
            result = serializer.save(
                performed_by=request.user,
            )
        except AdminDashboardNotificationRetryException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = AdminDashboardBulkNotificationRetryResponseSerializer(
            result,
            context={"request": request},
        )
        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


class AdminDashboardLogListAPIView(ListAPIView):
    """
    API endpoint for listing admin dashboard logs.
    """

    serializer_class = AdminDashboardLogListSerializer
    permission_classes = [IsAuthenticated, CanAccessAdminDashboard]
    pagination_class = AdminDashboardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdminDashboardLogFilter

    def get_queryset(self):
        return AdminDashboardLog.objects.select_related(
            "performed_by",
        ).order_by("-created_at")


class AdminDashboardLogDetailAPIView(RetrieveAPIView):
    """
    API endpoint for retrieving admin dashboard log details.
    """

    serializer_class = AdminDashboardLogDetailSerializer
    permission_classes = [IsAuthenticated, CanAccessAdminDashboardObject]
    lookup_url_kwarg = "log_id"

    def get_queryset(self):
        return AdminDashboardLog.objects.select_related(
            "performed_by",
            "lifecycle",
        ).prefetch_related(
            "events",
        )

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj


class AdminDashboardEventListAPIView(ListAPIView):
    """
    API endpoint for listing admin dashboard events.
    """

    serializer_class = AdminDashboardEventSerializer
    permission_classes = [IsAuthenticated, CanAccessAdminDashboard]
    pagination_class = AdminDashboardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdminDashboardEventFilter

    def get_queryset(self):
        return AdminDashboardEvent.objects.select_related(
            "performed_by",
            "related_log",
        ).order_by("-created_at")