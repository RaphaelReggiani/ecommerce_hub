from rest_framework import serializers

from ech.analytics.models import (
    AnalyticsEvent,
    AnalyticsSnapshot,
    AnalyticsSnapshotLifecycle,
)
from ech.analytics.services.analytic_snapshot_refresh_service import (
    AnalyticsSnapshotRefreshService,
)


class AnalyticsSnapshotLifecycleSerializer(serializers.ModelSerializer):
    """
    Serializer for analytics snapshot lifecycle timestamps.
    """

    class Meta:
        model = AnalyticsSnapshotLifecycle
        fields = [
            "generation_started_at",
            "generation_completed_at",
            "refreshed_at",
            "failed_at",
            "created_at",
            "updated_at",
        ]


class AnalyticsEventSerializer(serializers.ModelSerializer):
    """
    Serializer for analytics events.
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
        model = AnalyticsEvent
        fields = [
            "id",
            "event_type",
            "performed_by",
            "performed_by_name",
            "performed_by_email",
            "metadata",
            "created_at",
        ]


class AnalyticsSnapshotListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer used for analytics snapshot list endpoints.
    Suitable for management dashboards and paginated listings.
    """

    generated_by_name = serializers.CharField(
        source="generated_by.user_name",
        read_only=True,
    )
    generated_by_email = serializers.CharField(
        source="generated_by.user_email",
        read_only=True,
    )

    class Meta:
        model = AnalyticsSnapshot
        fields = [
            "id",
            "period_type",
            "period_start",
            "period_end",
            "total_orders",
            "total_revenue",
            "total_refunds",
            "net_revenue",
            "products_sold",
            "active_customers",
            "total_registered_users",
            "total_reviews",
            "average_rating",
            "generated_by",
            "generated_by_name",
            "generated_by_email",
            "created_at",
            "updated_at",
        ]


class AnalyticsSnapshotDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer used for analytics snapshot detail endpoints.
    """

    generated_by_name = serializers.CharField(
        source="generated_by.user_name",
        read_only=True,
    )
    generated_by_email = serializers.CharField(
        source="generated_by.user_email",
        read_only=True,
    )

    lifecycle = AnalyticsSnapshotLifecycleSerializer(read_only=True)
    events = AnalyticsEventSerializer(many=True, read_only=True)

    class Meta:
        model = AnalyticsSnapshot
        fields = [
            "id",
            "period_type",
            "period_start",
            "period_end",
            "total_orders",
            "orders_pending",
            "orders_processing",
            "orders_shipped",
            "orders_delivered",
            "orders_cancelled",
            "total_revenue",
            "total_refunds",
            "net_revenue",
            "payments_captured",
            "payments_failed",
            "payments_refunded",
            "shipments_in_transit",
            "shipments_delivered",
            "shipments_failed",
            "products_sold",
            "top_product_id",
            "active_customers",
            "new_customers",
            "total_registered_users",
            "active_users",
            "inactive_users",
            "confirmed_users",
            "unconfirmed_users",
            "staff_users",
            "customer_users",
            "total_reviews",
            "approved_reviews",
            "rejected_reviews",
            "hidden_reviews",
            "cancelled_reviews",
            "verified_purchase_reviews",
            "average_rating",
            "low_rated_products_count",
            "high_rated_products_count",
            "generated_by",
            "generated_by_name",
            "generated_by_email",
            "metadata",
            "lifecycle",
            "events",
            "created_at",
            "updated_at",
        ]


class AnalyticsSnapshotRefreshSerializer(serializers.Serializer):
    """
    Serializer responsible for validating analytics snapshot refresh payload
    and delegating business logic to AnalyticsSnapshotRefreshService.
    """

    metadata = serializers.JSONField(required=False)

    def create(self, validated_data):
        """
        Refresh an analytics snapshot through the service layer.
        """
        snapshot = validated_data["snapshot"]
        performed_by = validated_data.get("performed_by")

        return AnalyticsSnapshotRefreshService.refresh_snapshot(
            snapshot=snapshot,
            performed_by=performed_by,
            metadata=validated_data.get("metadata"),
        )


class AnalyticsOrdersSummarySerializer(serializers.Serializer):
    """
    Nested serializer for order summary metrics inside dashboard responses.
    """

    total_orders = serializers.IntegerField()
    orders_pending = serializers.IntegerField()
    orders_processing = serializers.IntegerField()
    orders_shipped = serializers.IntegerField()
    orders_delivered = serializers.IntegerField()
    orders_cancelled = serializers.IntegerField()


class AnalyticsRevenueSummarySerializer(serializers.Serializer):
    """
    Nested serializer for revenue summary metrics inside dashboard responses.
    """

    total_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_refunds = serializers.DecimalField(max_digits=14, decimal_places=2)
    net_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)


class AnalyticsPaymentsSummarySerializer(serializers.Serializer):
    """
    Nested serializer for payment summary metrics inside dashboard responses.
    """

    payments_captured = serializers.IntegerField()
    payments_failed = serializers.IntegerField()
    payments_refunded = serializers.IntegerField()


class AnalyticsShippingSummarySerializer(serializers.Serializer):
    """
    Nested serializer for shipping summary metrics inside dashboard responses.
    """

    shipments_in_transit = serializers.IntegerField()
    shipments_delivered = serializers.IntegerField()
    shipments_failed = serializers.IntegerField()


class AnalyticsProductsSummarySerializer(serializers.Serializer):
    """
    Nested serializer for product summary metrics inside dashboard responses.
    """

    products_sold = serializers.IntegerField()
    top_product_id = serializers.UUIDField(allow_null=True)


class AnalyticsCustomersSummarySerializer(serializers.Serializer):
    """
    Nested serializer for customer summary metrics inside dashboard responses.
    """

    active_customers = serializers.IntegerField()
    new_customers = serializers.IntegerField()


class AnalyticsUsersSummarySerializer(serializers.Serializer):
    """
    Nested serializer for user summary metrics inside dashboard responses.
    """

    total_registered_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    inactive_users = serializers.IntegerField()
    confirmed_users = serializers.IntegerField()
    unconfirmed_users = serializers.IntegerField()
    staff_users = serializers.IntegerField()
    customer_users = serializers.IntegerField()


class AnalyticsReviewsSummarySerializer(serializers.Serializer):
    """
    Nested serializer for review summary metrics inside dashboard responses.
    """

    total_reviews = serializers.IntegerField()
    approved_reviews = serializers.IntegerField()
    rejected_reviews = serializers.IntegerField()
    hidden_reviews = serializers.IntegerField()
    cancelled_reviews = serializers.IntegerField()
    verified_purchase_reviews = serializers.IntegerField()
    average_rating = serializers.DecimalField(max_digits=4, decimal_places=2)
    low_rated_products_count = serializers.IntegerField()
    high_rated_products_count = serializers.IntegerField()


class AnalyticsDashboardSummarySerializer(serializers.Serializer):
    """
    Serializer for analytics dashboard summary responses.
    """

    source = serializers.CharField()
    snapshot_id = serializers.UUIDField(allow_null=True)
    period_type = serializers.CharField(allow_null=True)
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()
    orders = AnalyticsOrdersSummarySerializer()
    revenue = AnalyticsRevenueSummarySerializer()
    payments = AnalyticsPaymentsSummarySerializer()
    shipping = AnalyticsShippingSummarySerializer()
    products = AnalyticsProductsSummarySerializer()
    customers = AnalyticsCustomersSummarySerializer()
    users = AnalyticsUsersSummarySerializer()
    reviews = AnalyticsReviewsSummarySerializer()


class AnalyticsSalesOverviewSerializer(serializers.Serializer):
    """
    Serializer for sales overview analytics responses.
    """

    source = serializers.CharField()
    snapshot_id = serializers.UUIDField(allow_null=True)
    period_type = serializers.CharField(allow_null=True)
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()
    total_orders = serializers.IntegerField()
    delivered_orders = serializers.IntegerField()
    cancelled_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_refunds = serializers.DecimalField(max_digits=14, decimal_places=2)
    net_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)
    average_order_value = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    payments_captured = serializers.IntegerField()
    payments_refunded = serializers.IntegerField()


class AnalyticsOrderFunnelSerializer(serializers.Serializer):
    """
    Serializer for order funnel analytics responses.
    """

    source = serializers.CharField()
    snapshot_id = serializers.UUIDField(allow_null=True)
    period_type = serializers.CharField(allow_null=True)
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()
    total_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    processing_orders = serializers.IntegerField()
    shipped_orders = serializers.IntegerField()
    delivered_orders = serializers.IntegerField()
    cancelled_orders = serializers.IntegerField()
    delivered_rate = serializers.FloatField()
    cancelled_rate = serializers.FloatField()


class AnalyticsProductPerformanceSerializer(serializers.Serializer):
    """
    Serializer for product performance analytics responses.
    """

    source = serializers.CharField()
    snapshot_id = serializers.UUIDField(allow_null=True)
    period_type = serializers.CharField(allow_null=True)
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()
    products_sold = serializers.IntegerField()
    top_product_id = serializers.UUIDField(allow_null=True)


class AnalyticsCustomerSummarySerializer(serializers.Serializer):
    """
    Serializer for customer summary analytics responses.
    """

    source = serializers.CharField()
    snapshot_id = serializers.UUIDField(allow_null=True)
    period_type = serializers.CharField(allow_null=True)
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()
    active_customers = serializers.IntegerField()
    new_customers = serializers.IntegerField()
    customer_growth = serializers.IntegerField()
    repeat_customer_rate = serializers.FloatField()


class AnalyticsUserOverviewSerializer(serializers.Serializer):
    """
    Serializer for user overview analytics responses.
    """

    source = serializers.CharField()
    snapshot_id = serializers.UUIDField(allow_null=True)
    period_type = serializers.CharField(allow_null=True)
    period_start = serializers.DateTimeField(allow_null=True)
    period_end = serializers.DateTimeField()
    total_registered_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    inactive_users = serializers.IntegerField()
    confirmed_users = serializers.IntegerField()
    unconfirmed_users = serializers.IntegerField()
    staff_users = serializers.IntegerField()
    customer_users = serializers.IntegerField()


class AnalyticsPaymentOverviewSerializer(serializers.Serializer):
    """
    Serializer for payment overview analytics responses.
    """

    source = serializers.CharField()
    snapshot_id = serializers.UUIDField(allow_null=True)
    period_type = serializers.CharField(allow_null=True)
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()
    payments_captured = serializers.IntegerField()
    payments_failed = serializers.IntegerField()
    payments_refunded = serializers.IntegerField()


class AnalyticsShippingOverviewSerializer(serializers.Serializer):
    """
    Serializer for shipping overview analytics responses.
    """

    source = serializers.CharField()
    snapshot_id = serializers.UUIDField(allow_null=True)
    period_type = serializers.CharField(allow_null=True)
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()
    shipments_in_transit = serializers.IntegerField()
    shipments_delivered = serializers.IntegerField()
    shipments_failed = serializers.IntegerField()


class AnalyticsReviewOverviewSerializer(serializers.Serializer):
    """
    Serializer for review overview analytics responses.
    """

    source = serializers.CharField()
    snapshot_id = serializers.UUIDField(allow_null=True)
    period_type = serializers.CharField(allow_null=True)
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()
    total_reviews = serializers.IntegerField()
    approved_reviews = serializers.IntegerField()
    rejected_reviews = serializers.IntegerField()
    hidden_reviews = serializers.IntegerField()
    cancelled_reviews = serializers.IntegerField()
    verified_purchase_reviews = serializers.IntegerField()
    average_rating = serializers.DecimalField(max_digits=4, decimal_places=2)
    low_rated_products_count = serializers.IntegerField()
    high_rated_products_count = serializers.IntegerField()