from django.contrib.auth import get_user_model

from rest_framework import serializers

from ech.notifications.models import (
    Notification,
    NotificationLifecycle,
    NotificationDelivery,
    NotificationEvent,
)
from ech.notifications.services.notification_creation_service import (
    NotificationCreationService,
)


User = get_user_model()


class CreateNotificationSerializer(serializers.Serializer):
    """
    Serializer responsible for validating notification creation payload
    and delegating business logic to NotificationCreationService.
    """

    recipient_id = serializers.IntegerField()

    channel = serializers.ChoiceField(
        choices=Notification._meta.get_field("channel").choices,
    )

    notification_type = serializers.CharField(max_length=100)

    title = serializers.CharField(max_length=255)

    message = serializers.CharField()

    priority = serializers.ChoiceField(
        choices=Notification._meta.get_field("priority").choices,
        required=False,
        default=Notification.PRIORITY_NORMAL,
    )

    source_module = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
    )

    source_event = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
    )

    source_object_id = serializers.CharField(
        max_length=64,
        required=False,
        allow_blank=True,
    )

    scheduled_for = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )

    metadata = serializers.JSONField(
        required=False,
        allow_null=True,
    )

    idempotency_key = serializers.UUIDField(
        required=False,
        allow_null=True,
    )

    def validate_recipient_id(self, value):
        """
        Ensure recipient exists.
        """
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("Recipient not found.")
        return value

    def validate(self, attrs):
        """
        Resolve recipient object for domain service usage.
        """
        recipient = User.objects.filter(id=attrs["recipient_id"]).first()

        if recipient is None:
            raise serializers.ValidationError(
                {"recipient_id": "Recipient not found."}
            )

        attrs["recipient"] = recipient
        return attrs

    def create(self, validated_data):
        """
        Create notification through the domain service.
        """
        request = self.context["request"]

        return NotificationCreationService.create_notification(
            recipient=validated_data["recipient"],
            notification_type=validated_data["notification_type"],
            title=validated_data["title"],
            message=validated_data["message"],
            channel=validated_data["channel"],
            priority=validated_data.get(
                "priority",
                Notification.PRIORITY_NORMAL,
            ),
            source_module=validated_data.get("source_module", ""),
            source_event=validated_data.get("source_event", ""),
            source_object_id=validated_data.get("source_object_id", ""),
            scheduled_for=validated_data.get("scheduled_for"),
            metadata=validated_data.get("metadata"),
            idempotency_key=validated_data.get("idempotency_key"),
            created_by=request.user,
            performed_by=request.user,
        )


class NotificationLifecycleSerializer(serializers.ModelSerializer):
    """
    Serializer for notification lifecycle timestamps.
    """

    class Meta:
        model = NotificationLifecycle
        fields = [
            "dispatched_at",
            "read_at",
            "archived_at",
            "cancelled_at",
            "failed_at",
            "created_at",
            "updated_at",
        ]


class NotificationDeliverySerializer(serializers.ModelSerializer):
    """
    Serializer for notification delivery attempts.
    """

    performed_by_name = serializers.CharField(
        source="performed_by.user_name",
        read_only=True,
    )
    performed_by_email = serializers.CharField(
        source="performed_by.user_email",
        read_only=True,
    )

    class Meta:
        model = NotificationDelivery
        fields = [
            "id",
            "channel",
            "status",
            "provider_name",
            "recipient_address",
            "external_message_id",
            "failure_code",
            "failure_message",
            "metadata",
            "performed_by",
            "performed_by_name",
            "performed_by_email",
            "processed_at",
            "created_at",
        ]


class NotificationEventSerializer(serializers.ModelSerializer):
    """
    Serializer for notification events.
    """

    performed_by_name = serializers.CharField(
        source="performed_by.user_name",
        read_only=True,
    )

    performed_by_email = serializers.CharField(
        source="performed_by.user_email",
        read_only=True,
    )

    class Meta:
        model = NotificationEvent
        fields = [
            "id",
            "event_type",
            "performed_by",
            "performed_by_name",
            "performed_by_email",
            "metadata",
            "created_at",
        ]


class NotificationListSerializer(serializers.ModelSerializer):
    """
    Serializer used for recipient notification list endpoints.
    """

    recipient_name = serializers.CharField(
        source="recipient.user_name",
        read_only=True,
    )

    recipient_email = serializers.CharField(
        source="recipient.user_email",
        read_only=True,
    )

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "recipient_name",
            "recipient_email",
            "channel",
            "notification_type",
            "title",
            "priority",
            "status",
            "scheduled_for",
            "created_at",
        ]


class NotificationManagementListSerializer(serializers.ModelSerializer):
    """
    Serializer used for staff notification management list endpoints.
    """

    recipient_name = serializers.CharField(
        source="recipient.user_name",
        read_only=True,
    )

    recipient_email = serializers.CharField(
        source="recipient.user_email",
        read_only=True,
    )

    created_by_name = serializers.CharField(
        source="created_by.user_name",
        read_only=True,
    )
    created_by_email = serializers.CharField(
        source="created_by.user_email",
        read_only=True,
    )

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "recipient_name",
            "recipient_email",
            "created_by",
            "created_by_name",
            "created_by_email",
            "channel",
            "notification_type",
            "title",
            "priority",
            "status",
            "source_module",
            "source_event",
            "source_object_id",
            "scheduled_for",
            "created_at",
        ]


class NotificationDetailSerializer(serializers.ModelSerializer):
    """
    Serializer used for recipient notification detail endpoints.
    """

    recipient_name = serializers.CharField(
        source="recipient.user_name",
        read_only=True,
    )

    recipient_email = serializers.CharField(
        source="recipient.user_email",
        read_only=True,
    )

    lifecycle = NotificationLifecycleSerializer(read_only=True)

    events = NotificationEventSerializer(
        many=True,
        read_only=True,
    )

    deliveries = NotificationDeliverySerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "recipient_name",
            "recipient_email",
            "channel",
            "notification_type",
            "title",
            "message",
            "priority",
            "status",
            "failure_code",
            "failure_message",
            "source_module",
            "source_event",
            "source_object_id",
            "metadata",
            "scheduled_for",
            "lifecycle",
            "events",
            "deliveries",
            "created_at",
            "updated_at",
        ]


class NotificationManagementDetailSerializer(serializers.ModelSerializer):
    """
    Serializer used for staff notification management detail endpoints.
    """

    recipient_name = serializers.CharField(
        source="recipient.user_name",
        read_only=True,
    )

    recipient_email = serializers.CharField(
        source="recipient.user_email",
        read_only=True,
    )

    created_by_name = serializers.CharField(
        source="created_by.user_name",
        read_only=True,
    )
    created_by_email = serializers.CharField(
        source="created_by.user_email",
        read_only=True,
    )

    lifecycle = NotificationLifecycleSerializer(read_only=True)

    events = NotificationEventSerializer(
        many=True,
        read_only=True,
    )

    deliveries = NotificationDeliverySerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "recipient_name",
            "recipient_email",
            "created_by",
            "created_by_name",
            "created_by_email",
            "channel",
            "notification_type",
            "title",
            "message",
            "priority",
            "status",
            "failure_code",
            "failure_message",
            "source_module",
            "source_event",
            "source_object_id",
            "metadata",
            "scheduled_for",
            "lifecycle",
            "events",
            "deliveries",
            "created_at",
            "updated_at",
        ]