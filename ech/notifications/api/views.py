from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound

from django_filters.rest_framework import DjangoFilterBackend

from ech.notifications.constants.messages import (
    MSG_NOTIFICATION_NOT_FOUND,
)
from ech.notifications.exceptions import (
    NotificationException,
    NotificationNotFoundException,
)
from ech.notifications.models import Notification
from ech.notifications.selectors import (
    get_notification_by_id,
    list_user_notifications,
    list_management_notifications,
)
from ech.notifications.filters import (
    NotificationFilter,
    NotificationManagementFilter,
)
from ech.notifications.api.permissions import (
    CanManageNotifications,
    IsNotificationRecipientOrCanManageNotifications,
)
from ech.notifications.api.pagination import NotificationsPagination
from ech.notifications.api.serializers import (
    CreateNotificationSerializer,
    NotificationListSerializer,
    NotificationDetailSerializer,
    NotificationManagementListSerializer,
    NotificationManagementDetailSerializer,
)
from ech.notifications.services.notification_status_service import (
    NotificationStatusService,
)
from ech.notifications.services.notification_delivery_service import (
    NotificationDeliveryService,
)
from ech.notifications.services.notification_cancellation_service import (
    NotificationCancellationService,
)


class NotificationCreateAPIView(CreateAPIView):
    """
    API endpoint for creating notifications.

    Restricted to roles allowed to manage notifications.
    """

    serializer_class = CreateNotificationSerializer
    permission_classes = [IsAuthenticated, CanManageNotifications]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        try:
            notification = serializer.save()
        except NotificationException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = NotificationManagementDetailSerializer(
            notification,
            context={"request": request},
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class NotificationListAPIView(ListAPIView):
    """
    API endpoint for listing notifications of the authenticated user.
    """

    serializer_class = NotificationListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NotificationsPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = NotificationFilter

    def get_queryset(self):
        return list_user_notifications(user=self.request.user)


class NotificationDetailAPIView(RetrieveAPIView):
    """
    API endpoint for retrieving a specific notification detail.
    """

    serializer_class = NotificationDetailSerializer
    permission_classes = [
        IsAuthenticated,
        IsNotificationRecipientOrCanManageNotifications,
    ]
    lookup_url_kwarg = "notification_id"

    def get_object(self):
        notification_id = self.kwargs.get(self.lookup_url_kwarg)

        try:
            notification = get_notification_by_id(
                notification_id=notification_id,
            )
        except NotificationNotFoundException:
            raise NotFound(MSG_NOTIFICATION_NOT_FOUND)

        self.check_object_permissions(self.request, notification)
        return notification


class NotificationMarkAsReadAPIView(APIView):
    """
    API endpoint for marking a notification as read.
    """

    permission_classes = [
        IsAuthenticated,
        IsNotificationRecipientOrCanManageNotifications,
    ]

    def post(self, request, notification_id, *args, **kwargs):
        try:
            notification = get_notification_by_id(
                notification_id=notification_id,
            )
        except NotificationNotFoundException:
            raise NotFound(MSG_NOTIFICATION_NOT_FOUND)

        self.check_object_permissions(request, notification)

        try:
            if notification.status != Notification.STATUS_READ:
                notification = NotificationStatusService.mark_as_read(
                    notification=notification,
                    performed_by=request.user,
                )
        except NotificationException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = NotificationDetailSerializer(
            notification,
            context={"request": request},
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


class NotificationArchiveAPIView(APIView):
    """
    API endpoint for archiving a notification.
    """

    permission_classes = [
        IsAuthenticated,
        IsNotificationRecipientOrCanManageNotifications,
    ]

    def post(self, request, notification_id, *args, **kwargs):
        try:
            notification = get_notification_by_id(
                notification_id=notification_id,
            )
        except NotificationNotFoundException:
            raise NotFound(MSG_NOTIFICATION_NOT_FOUND)

        self.check_object_permissions(request, notification)

        try:
            if notification.status != Notification.STATUS_ARCHIVED:
                notification = NotificationStatusService.archive(
                    notification=notification,
                    performed_by=request.user,
                )
        except NotificationException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = NotificationDetailSerializer(
            notification,
            context={"request": request},
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


class NotificationDispatchAPIView(APIView):
    """
    API endpoint for dispatching a notification.

    Restricted to roles allowed to manage notifications.
    """

    permission_classes = [IsAuthenticated, CanManageNotifications]

    def post(self, request, notification_id, *args, **kwargs):
        try:
            notification = get_notification_by_id(
                notification_id=notification_id,
            )
        except NotificationNotFoundException:
            raise NotFound(MSG_NOTIFICATION_NOT_FOUND)

        try:
            if notification.status == Notification.STATUS_PENDING:
                notification = NotificationDeliveryService.dispatch_notification(
                    notification=notification,
                    performed_by=request.user,
                )
        except NotificationException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = NotificationDetailSerializer(
            notification,
            context={"request": request},
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


class NotificationCancelAPIView(APIView):
    """
    API endpoint for cancelling a notification.

    Restricted to roles allowed to manage notifications.
    """

    permission_classes = [IsAuthenticated, CanManageNotifications]

    def post(self, request, notification_id, *args, **kwargs):
        try:
            notification = get_notification_by_id(
                notification_id=notification_id,
            )
        except NotificationNotFoundException:
            raise NotFound(MSG_NOTIFICATION_NOT_FOUND)

        try:
            if notification.status != Notification.STATUS_CANCELLED:
                notification = NotificationCancellationService.cancel_notification(
                    notification=notification,
                    performed_by=request.user,
                )
        except NotificationException as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = NotificationDetailSerializer(
            notification,
            context={"request": request},
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


class NotificationManagementListAPIView(ListAPIView):
    """
    API endpoint for staff notification management listing.
    """

    serializer_class = NotificationManagementListSerializer
    permission_classes = [IsAuthenticated, CanManageNotifications]
    pagination_class = NotificationsPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = NotificationManagementFilter

    def get_queryset(self):
        return list_management_notifications()


class NotificationManagementDetailAPIView(RetrieveAPIView):
    """
    API endpoint for staff notification management detail.
    """

    serializer_class = NotificationManagementDetailSerializer
    permission_classes = [IsAuthenticated, CanManageNotifications]
    lookup_url_kwarg = "notification_id"

    def get_object(self):
        notification_id = self.kwargs.get(self.lookup_url_kwarg)

        try:
            notification = get_notification_by_id(
                notification_id=notification_id,
            )
        except NotificationNotFoundException:
            raise NotFound(MSG_NOTIFICATION_NOT_FOUND)

        return notification