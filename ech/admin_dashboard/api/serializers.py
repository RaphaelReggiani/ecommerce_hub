from rest_framework import serializers

from ech.admin_dashboard.models import (
    AdminDashboardEvent,
    AdminDashboardLifecycle,
    AdminDashboardLog,
)
from ech.admin_dashboard.services.admin_dashboard_bulk_notification_retry_service import (
    AdminDashboardBulkNotificationRetryService,
)
from ech.admin_dashboard.services.admin_dashboard_bulk_order_actions_service import (
    AdminDashboardBulkOrderActionsService,
)
from ech.admin_dashboard.services.admin_dashboard_bulk_review_moderation_service import (
    AdminDashboardBulkReviewModerationService,
)


class AdminDashboardLifecycleSerializer(serializers.ModelSerializer):
    """
    Serializer for admin dashboard lifecycle timestamps.
    """

    class Meta:
        model = AdminDashboardLifecycle
        fields = [
            "started_at",
            "completed_at",
            "failed_at",
            "created_at",
            "updated_at",
        ]


class AdminDashboardEventSerializer(serializers.ModelSerializer):
    """
    Serializer for admin dashboard events.
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
        model = AdminDashboardEvent
        fields = [
            "id",
            "event_type",
            "performed_by",
            "performed_by_name",
            "performed_by_email",
            "related_log",
            "metadata",
            "created_at",
        ]


class AdminDashboardLogListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer used for admin dashboard log listings.
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
        model = AdminDashboardLog
        fields = [
            "id",
            "action_type",
            "performed_by",
            "performed_by_name",
            "performed_by_email",
            "target_object_id",
            "target_module",
            "created_at",
        ]


class AdminDashboardLogDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer used for admin dashboard log detail endpoints.
    """

    performed_by_name = serializers.CharField(
        source="performed_by.user_name",
        read_only=True,
    )
    performed_by_email = serializers.CharField(
        source="performed_by.user_email",
        read_only=True,
    )
    lifecycle = AdminDashboardLifecycleSerializer(read_only=True)
    events = AdminDashboardEventSerializer(many=True, read_only=True)

    class Meta:
        model = AdminDashboardLog
        fields = [
            "id",
            "action_type",
            "performed_by",
            "performed_by_name",
            "performed_by_email",
            "target_object_id",
            "target_module",
            "metadata",
            "lifecycle",
            "events",
            "created_at",
        ]


class AdminDashboardOrdersSummarySerializer(serializers.Serializer):
    """
    Nested serializer for order summary metrics.
    """

    total_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    processing_orders = serializers.IntegerField()
    shipped_orders = serializers.IntegerField()
    delivered_orders = serializers.IntegerField()
    cancelled_orders = serializers.IntegerField()


class AdminDashboardPaymentsSummarySerializer(serializers.Serializer):
    """
    Nested serializer for payment summary metrics.
    """

    total_payments = serializers.IntegerField()
    captured_payments = serializers.IntegerField()
    failed_payments = serializers.IntegerField()
    refunded_payments = serializers.IntegerField()
    partially_refunded_payments = serializers.IntegerField()


class AdminDashboardShippingSummarySerializer(serializers.Serializer):
    """
    Nested serializer for shipping summary metrics.
    """

    total_shipments = serializers.IntegerField()
    pending_shipments = serializers.IntegerField()
    in_transit_shipments = serializers.IntegerField()
    delivered_shipments = serializers.IntegerField()
    failed_shipments = serializers.IntegerField()
    returned_shipments = serializers.IntegerField()


class AdminDashboardUsersSummarySerializer(serializers.Serializer):
    """
    Nested serializer for user summary metrics.
    """

    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    inactive_users = serializers.IntegerField()
    staff_users = serializers.IntegerField()
    customer_users = serializers.IntegerField()
    confirmed_users = serializers.IntegerField()
    unconfirmed_users = serializers.IntegerField()


class AdminDashboardReviewsSummarySerializer(serializers.Serializer):
    """
    Nested serializer for review summary metrics.
    """

    total_reviews = serializers.IntegerField()
    pending_reviews = serializers.IntegerField()
    approved_reviews = serializers.IntegerField()
    rejected_reviews = serializers.IntegerField()
    hidden_reviews = serializers.IntegerField()
    cancelled_reviews = serializers.IntegerField()


class AdminDashboardProductsSummarySerializer(serializers.Serializer):
    """
    Nested serializer for product summary metrics.
    """

    total_products = serializers.IntegerField()
    active_products = serializers.IntegerField()
    inactive_products = serializers.IntegerField()


class AdminDashboardSummarySerializer(serializers.Serializer):
    """
    Serializer for admin dashboard summary responses.
    """

    orders = AdminDashboardOrdersSummarySerializer()
    payments = AdminDashboardPaymentsSummarySerializer()
    shipping = AdminDashboardShippingSummarySerializer()
    users = AdminDashboardUsersSummarySerializer()
    reviews = AdminDashboardReviewsSummarySerializer()
    products = AdminDashboardProductsSummarySerializer()


class AdminDashboardOrdersOperationalMetricsSerializer(serializers.Serializer):
    """
    Nested serializer for order operational monitoring metrics.
    """

    pending_orders = serializers.IntegerField()
    processing_orders = serializers.IntegerField()
    cancelled_orders = serializers.IntegerField()


class AdminDashboardPaymentsOperationalMetricsSerializer(serializers.Serializer):
    """
    Nested serializer for payment operational monitoring metrics.
    """

    failed_payments = serializers.IntegerField()
    processing_payments = serializers.IntegerField()
    refunded_payments = serializers.IntegerField()


class AdminDashboardShippingOperationalMetricsSerializer(serializers.Serializer):
    """
    Nested serializer for shipping operational monitoring metrics.
    """

    delayed_shipments = serializers.IntegerField()
    failed_shipments = serializers.IntegerField()
    in_transit_shipments = serializers.IntegerField()


class AdminDashboardReviewsOperationalMetricsSerializer(serializers.Serializer):
    """
    Nested serializer for review operational monitoring metrics.
    """

    pending_moderation = serializers.IntegerField()
    flagged_reviews = serializers.IntegerField()
    hidden_reviews = serializers.IntegerField()


class AdminDashboardNotificationsOperationalMetricsSerializer(serializers.Serializer):
    """
    Nested serializer for notification operational monitoring metrics.
    """

    failed_notifications = serializers.IntegerField()
    pending_notifications = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()


class AdminDashboardProductsOperationalMetricsSerializer(serializers.Serializer):
    """
    Nested serializer for product operational monitoring metrics.
    """

    low_stock_products = serializers.IntegerField()
    out_of_stock_products = serializers.IntegerField()
    products_without_images = serializers.IntegerField()


class AdminDashboardOperationalMetricsSerializer(serializers.Serializer):
    """
    Serializer for admin dashboard operational metrics responses.
    """

    orders = AdminDashboardOrdersOperationalMetricsSerializer()
    payments = AdminDashboardPaymentsOperationalMetricsSerializer()
    shipping = AdminDashboardShippingOperationalMetricsSerializer()
    reviews = AdminDashboardReviewsOperationalMetricsSerializer()
    notifications = AdminDashboardNotificationsOperationalMetricsSerializer()
    products = AdminDashboardProductsOperationalMetricsSerializer()


class AdminDashboardRecentActivityItemSerializer(serializers.Serializer):
    """
    Serializer for a single recent activity item.
    """

    source = serializers.CharField()
    type = serializers.CharField()
    entity_id = serializers.CharField()
    status = serializers.CharField(required=False, allow_null=True)
    action_type = serializers.CharField(required=False, allow_null=True)
    target_module = serializers.CharField(required=False, allow_null=True)
    created_at = serializers.DateTimeField(allow_null=True)


class AdminDashboardRecentActivitySerializer(serializers.Serializer):
    """
    Serializer for admin dashboard recent activity responses.
    """

    activities = AdminDashboardRecentActivityItemSerializer(many=True)
    total = serializers.IntegerField()
    limit = serializers.IntegerField()


class AdminDashboardAlertItemSerializer(serializers.Serializer):
    """
    Serializer for a single operational alert item.
    """

    type = serializers.CharField()
    severity = serializers.CharField()
    message = serializers.CharField()
    value = serializers.IntegerField()


class AdminDashboardAlertsSerializer(serializers.Serializer):
    """
    Serializer for admin dashboard operational alerts responses.
    """

    alerts = AdminDashboardAlertItemSerializer(many=True)
    total_alerts = serializers.IntegerField()
    critical_alerts = serializers.IntegerField()
    warning_alerts = serializers.IntegerField()
    info_alerts = serializers.IntegerField()


class AdminDashboardBulkOrderActionSerializer(serializers.Serializer):
    """
    Serializer responsible for validating bulk order action payloads
    and delegating business logic to AdminDashboardBulkOrderActionsService.
    """

    action_type = serializers.ChoiceField(
        choices=sorted(
            AdminDashboardBulkOrderActionsService.ALLOWED_ACTIONS
        )
    )
    order_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
    )

    def create(self, validated_data):
        """
        Execute a bulk administrative action on orders.
        """
        performed_by = validated_data.get("performed_by")

        return AdminDashboardBulkOrderActionsService.execute_bulk_action(
            action_type=validated_data["action_type"],
            order_ids=validated_data["order_ids"],
            performed_by=performed_by,
        )


class AdminDashboardBulkOrderActionResponseSerializer(serializers.Serializer):
    """
    Serializer for bulk order action responses.
    """

    action = serializers.CharField()
    processed_orders = serializers.ListField(
        child=serializers.UUIDField()
    )
    total_processed = serializers.IntegerField()


class AdminDashboardBulkReviewModerationSerializer(serializers.Serializer):
    """
    Serializer responsible for validating bulk review moderation payloads
    and delegating business logic to
    AdminDashboardBulkReviewModerationService.
    """

    moderation_action = serializers.ChoiceField(
        choices=sorted(
            AdminDashboardBulkReviewModerationService.ALLOWED_ACTIONS
        )
    )
    review_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
    )
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    def create(self, validated_data):
        """
        Execute a bulk moderation action on reviews.
        """
        performed_by = validated_data.get("performed_by")

        return AdminDashboardBulkReviewModerationService.execute_bulk_moderation(
            moderation_action=validated_data["moderation_action"],
            review_ids=validated_data["review_ids"],
            performed_by=performed_by,
            reason=validated_data.get("reason", ""),
        )


class AdminDashboardBulkReviewModerationResponseSerializer(serializers.Serializer):
    """
    Serializer for bulk review moderation responses.
    """

    moderation_action = serializers.CharField()
    processed_reviews = serializers.ListField(
        child=serializers.UUIDField()
    )
    total_processed = serializers.IntegerField()


class AdminDashboardBulkNotificationRetrySerializer(serializers.Serializer):
    """
    Serializer responsible for validating notification retry payloads
    and delegating business logic to
    AdminDashboardBulkNotificationRetryService.
    """

    notification_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
    )

    def create(self, validated_data):
        """
        Retry failed notifications through the service layer.
        """
        performed_by = validated_data.get("performed_by")

        return AdminDashboardBulkNotificationRetryService.retry_notifications(
            notification_ids=validated_data["notification_ids"],
            performed_by=performed_by,
        )


class AdminDashboardBulkNotificationRetryResponseSerializer(serializers.Serializer):
    """
    Serializer for bulk notification retry responses.
    """

    retried_notifications = serializers.ListField(
        child=serializers.UUIDField()
    )
    total_retried = serializers.IntegerField()