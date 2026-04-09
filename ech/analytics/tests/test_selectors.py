import uuid
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ech.analytics.exceptions import AnalyticsSnapshotNotFoundException
from ech.analytics.models import (
    AnalyticsEvent,
    AnalyticsSnapshot,
    AnalyticsSnapshotLifecycle,
)
from ech.analytics.selectors import (
    analytics_snapshot_base_queryset,
    get_analytics_snapshot_by_id,
    get_analytics_snapshot_with_related,
    get_latest_analytics_snapshot_by_period_type,
    list_analytics_snapshots,
    list_analytics_snapshots_by_period_type,
    list_analytics_snapshots_by_period_range,
    list_recent_analytics_snapshots,
    order_analytics_base_queryset,
    list_orders_for_analytics,
    payment_analytics_base_queryset,
    list_payments_for_analytics,
    shipment_analytics_base_queryset,
    list_shipments_for_analytics,
    product_analytics_base_queryset,
    list_products_for_analytics,
    customer_analytics_base_queryset,
    list_customers_for_analytics,
    user_analytics_base_queryset,
    list_users_for_analytics,
    review_analytics_base_queryset,
    list_reviews_for_analytics,
    notification_analytics_base_queryset,
    list_notifications_for_analytics,
    search_analytics_snapshots,
)
from ech.notifications.models import (
    Notification,
    NotificationDelivery,
    NotificationEvent,
    NotificationLifecycle,
)
from ech.orders.models import (
    Order,
    OrderAddress,
    OrderEvent,
    OrderItem,
    OrderLifecycle,
    OrderNote,
    OrderTotals,
)
from ech.payments.models import (
    Payment,
    PaymentEvent,
    PaymentLifecycle,
    PaymentRefund,
    PaymentTransaction,
)
from ech.products.models import (
    Product,
    ProductEventLog,
    ProductInventory,
)
from ech.reviews.models import (
    Review,
    ReviewEvent,
    ReviewLifecycle,
)
from ech.shipping.models import (
    Shipment,
    ShipmentAddress,
    ShipmentEvent,
    ShipmentLifecycle,
    ShipmentNote,
    ShipmentTrackingUpdate,
)

User = get_user_model()


def passthrough_get_or_set(*, key, producer, timeout):
    return producer()


class BaseAnalyticsSelectorFactoryMixin:
    @staticmethod
    def unique_suffix():
        return uuid.uuid4().hex[:8]

    @classmethod
    def create_user(cls, **kwargs):
        suffix = cls.unique_suffix()

        data = {
            "email": f"user_{suffix}@test.com",
            "password": "StrongPassword123",
            "user_name": f"User {suffix}",
            "role": User.ROLE_CUSTOMER_USER,
            "is_active": True,
            "email_confirmed": True,
        }
        data.update(kwargs)
        return User.objects.create_user(**data)

    @classmethod
    def create_staff_user(cls, **kwargs):
        suffix = cls.unique_suffix()

        data = {
            "email": f"staff_{suffix}@company.com",
            "password": "StrongPassword123",
            "user_name": f"Staff {suffix}",
            "role": User.ROLE_ANALYTICS_STAFF,
            "is_active": True,
            "email_confirmed": True,
        }
        data.update(kwargs)
        return User.objects.create_user(**data)

    @classmethod
    def create_product(cls, **kwargs):
        sold_by = kwargs.pop("sold_by", None) or cls.create_staff_user()

        data = {
            "name": f"Product {cls.unique_suffix()}",
            "product_type": Product.PHONE,
            "brand": "Apple",
            "sold_by": sold_by,
            "description": "Product description",
            "technical_information": "Tech specs",
            "price": Decimal("5000.00"),
            "discount_price": Decimal("4500.00"),
            "is_active": True,
        }
        data.update(kwargs)
        return Product.objects.create(**data)

    @classmethod
    def create_product_with_related_data(cls, **kwargs):
        product = cls.create_product(**kwargs)

        ProductInventory.objects.create(
            product=product,
            quantity=10,
        )
        ProductEventLog.objects.create(
            product=product,
            event_type=ProductEventLog.EVENT_PRODUCT_CREATED,
        )

        return product

    @classmethod
    def create_order(cls, **kwargs):
        customer = kwargs.pop("customer", None) or cls.create_user()

        data = {
            "customer": customer,
            "status": Order.ORDER_STATUS_PENDING,
            "payment_status": Order.PAYMENT_STATUS_PENDING,
            "shipping_status": Order.SHIPPING_STATUS_PENDING,
            "currency": "USD",
        }
        data.update(kwargs)
        return Order.objects.create(**data)

    @classmethod
    def create_order_with_related_data(cls, **kwargs):
        product = kwargs.pop("product", None) or cls.create_product()
        order = cls.create_order(**kwargs)

        OrderTotals.objects.create(
            order=order,
            subtotal=Decimal("4500.00"),
            discount_total=Decimal("500.00"),
            tax_total=Decimal("0.00"),
            shipping_total=Decimal("0.00"),
            grand_total=Decimal("4500.00"),
        )
        OrderAddress.objects.create(
            order=order,
            full_name="Customer User",
            address_line="Av. Paulista, 1000",
            city="Sao Paulo",
            state="SP",
            country="Brazil",
            postal_code="01310-100",
            phone="11999999999",
        )
        OrderLifecycle.objects.create(order=order)
        OrderEvent.objects.create(
            order=order,
            event_type=OrderEvent.TYPE_CREATED,
        )
        OrderNote.objects.create(
            order=order,
            author=order.customer,
            message="Internal note",
            is_internal=True,
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name_snapshot=product.name,
            product_type_snapshot=product.product_type,
            brand_snapshot=product.brand,
            quantity=2,
            unit_price=Decimal("2500.00"),
            discount_price=Decimal("2250.00"),
            total_price=Decimal("4500.00"),
        )

        return order

    @classmethod
    def create_payment(cls, **kwargs):
        order = kwargs.pop("order", None) or cls.create_order()
        customer = kwargs.pop("customer", None) or order.customer

        data = {
            "order": order,
            "customer": customer,
            "payment_reference": f"PAY-{cls.unique_suffix().upper()}",
            "method": Payment.PAYMENT_METHOD_PIX,
            "status": Payment.PAYMENT_STATUS_CAPTURED,
            "amount": Decimal("4500.00"),
            "refunded_amount": Decimal("0.00"),
            "currency": "USD",
            "gateway_name": "stripe",
            "gateway_payment_id": f"GW-{cls.unique_suffix()}",
            "gateway_customer_id": f"CUST-{cls.unique_suffix()}",
            "metadata": {"source": "test"},
        }
        data.update(kwargs)
        return Payment.objects.create(**data)

    @classmethod
    def create_payment_with_related_data(cls, **kwargs):
        payment = cls.create_payment(**kwargs)

        PaymentLifecycle.objects.create(payment=payment)
        PaymentTransaction.objects.create(
            payment=payment,
            transaction_type=PaymentTransaction.TRANSACTION_TYPE_CHARGE,
            status=PaymentTransaction.TRANSACTION_STATUS_SUCCESS,
            amount=payment.amount,
            currency=payment.currency,
        )
        PaymentRefund.objects.create(
            payment=payment,
            amount=Decimal("100.00"),
            reason="Partial refund",
            status=PaymentRefund.REFUND_STATUS_PENDING,
        )
        PaymentEvent.objects.create(
            payment=payment,
            event_type=PaymentEvent.TYPE_CREATED,
        )

        return payment

    @classmethod
    def create_shipment(cls, **kwargs):
        order = kwargs.pop("order", None) or cls.create_order()
        customer = kwargs.pop("customer", None) or order.customer

        data = {
            "order": order,
            "customer": customer,
            "status": Shipment.STATUS_PENDING,
            "shipping_method": Shipment.METHOD_STANDARD,
            "carrier_name": "DHL",
            "tracking_code": f"TRACK-{cls.unique_suffix().upper()}",
            "external_reference": f"EXT-{cls.unique_suffix().upper()}",
            "shipping_cost": Decimal("25.00"),
            "currency": "USD",
            "estimated_delivery_date": timezone.now().date() + timedelta(days=5),
        }
        data.update(kwargs)
        return Shipment.objects.create(**data)

    @classmethod
    def create_shipment_with_related_data(cls, **kwargs):
        shipment = cls.create_shipment(**kwargs)

        ShipmentAddress.objects.create(
            shipment=shipment,
            full_name="Customer User",
            address_line="Av. Paulista, 1000",
            city="Sao Paulo",
            state="SP",
            country="Brazil",
            postal_code="01310-100",
            phone="11999999999",
        )
        ShipmentLifecycle.objects.create(
            shipment=shipment,
            preparing_at=timezone.now(),
        )
        ShipmentEvent.objects.create(
            shipment=shipment,
            event_type=ShipmentEvent.TYPE_CREATED,
        )
        ShipmentTrackingUpdate.objects.create(
            shipment=shipment,
            status=Shipment.STATUS_PENDING,
            location="Warehouse",
            description="Shipment created",
            event_at=timezone.now(),
        )
        ShipmentNote.objects.create(
            shipment=shipment,
            author=shipment.customer,
            message="Operational note",
            is_internal=True,
        )

        return shipment

    @classmethod
    def create_review(cls, **kwargs):
        customer = kwargs.pop("customer", None) or cls.create_user()
        product = kwargs.pop("product", None) or cls.create_product()

        data = {
            "customer": customer,
            "product": product,
            "rating": 5,
            "title": "Excellent",
            "comment": "Very good product",
            "status": Review.REVIEW_STATUS_APPROVED,
            "is_verified_purchase": True,
        }
        data.update(kwargs)
        return Review.objects.create(**data)

    @classmethod
    def create_review_with_related_data(cls, **kwargs):
        review = cls.create_review(**kwargs)

        ReviewLifecycle.objects.create(review=review)
        ReviewEvent.objects.create(
            review=review,
            event_type=ReviewEvent.TYPE_CREATED,
        )

        return review

    @classmethod
    def create_notification(cls, **kwargs):
        recipient = kwargs.pop("recipient", None) or cls.create_user()
        created_by = kwargs.pop("created_by", None) or cls.create_staff_user()

        data = {
            "recipient": recipient,
            "created_by": created_by,
            "notification_type": "order_shipped",
            "title": "Order update",
            "message": "Your order has been updated.",
            "status": Notification.STATUS_UNREAD,
            "channel": Notification.CHANNEL_IN_APP,
            "priority": Notification.PRIORITY_NORMAL,
            "source_module": "orders",
            "source_event": "order_shipped",
            "source_object_id": str(uuid.uuid4()),
            "metadata": {"source": "test"},
        }
        data.update(kwargs)
        return Notification.objects.create(**data)

    @classmethod
    def create_notification_with_related_data(cls, **kwargs):
        notification = cls.create_notification(**kwargs)

        NotificationLifecycle.objects.create(notification=notification)
        NotificationDelivery.objects.create(
            notification=notification,
            channel=NotificationDelivery.CHANNEL_IN_APP,
            status=NotificationDelivery.STATUS_DELIVERED,
            provider_name="in_app_provider",
        )
        NotificationEvent.objects.create(
            notification=notification,
            event_type=NotificationEvent.TYPE_CREATED,
        )

        return notification

    @classmethod
    def create_snapshot(cls, **kwargs):
        generated_by = kwargs.pop("generated_by", None) or cls.create_staff_user()
        now = timezone.now()

        data = {
            "period_type": AnalyticsSnapshot.PERIOD_DAILY,
            "period_start": now - timedelta(days=1),
            "period_end": now,
            "generated_by": generated_by,
            "total_orders": 10,
            "orders_pending": 1,
            "orders_processing": 2,
            "orders_shipped": 2,
            "orders_delivered": 4,
            "orders_cancelled": 1,
            "total_revenue": Decimal("1000.00"),
            "total_refunds": Decimal("100.00"),
            "net_revenue": Decimal("900.00"),
            "payments_captured": 7,
            "payments_failed": 1,
            "payments_refunded": 1,
            "shipments_in_transit": 2,
            "shipments_delivered": 4,
            "shipments_failed": 1,
            "products_sold": 15,
            "active_customers": 8,
            "new_customers": 3,
            "total_registered_users": 30,
            "active_users": 25,
            "inactive_users": 5,
            "confirmed_users": 24,
            "unconfirmed_users": 6,
            "staff_users": 5,
            "customer_users": 25,
            "total_reviews": 12,
            "approved_reviews": 8,
            "rejected_reviews": 1,
            "hidden_reviews": 1,
            "cancelled_reviews": 2,
            "verified_purchase_reviews": 7,
            "average_rating": Decimal("4.25"),
            "low_rated_products_count": 1,
            "high_rated_products_count": 3,
            "metadata": {"label": "daily snapshot"},
        }
        data.update(kwargs)
        return AnalyticsSnapshot.objects.create(**data)

    @classmethod
    def create_snapshot_with_related_data(cls, **kwargs):
        snapshot = cls.create_snapshot(**kwargs)

        AnalyticsSnapshotLifecycle.objects.create(
            snapshot=snapshot,
            generation_started_at=timezone.now(),
            generation_completed_at=timezone.now(),
        )
        AnalyticsEvent.objects.create(
            snapshot=snapshot,
            event_type=AnalyticsEvent.TYPE_SNAPSHOT_CREATED,
        )

        return snapshot


class AnalyticsSnapshotBaseQuerysetTestCase(
    BaseAnalyticsSelectorFactoryMixin,
    TestCase,
):
    def test_analytics_snapshot_base_queryset_applies_select_and_prefetch_related(self):
        queryset = analytics_snapshot_base_queryset()

        self.assertEqual(
            queryset.query.select_related,
            {
                "generated_by": {},
                "lifecycle": {},
            },
        )
        self.assertEqual(
            set(queryset._prefetch_related_lookups),
            {"events"},
        )


class AnalyticsSnapshotRetrievalSelectorTestCase(
    BaseAnalyticsSelectorFactoryMixin,
    TestCase,
):
    @classmethod
    def setUpTestData(cls):
        cls.snapshot = cls.create_snapshot_with_related_data()

    @patch(
        "ech.analytics.selectors.AnalyticsCacheService.get_snapshot_version",
        return_value=1,
    )
    @patch(
        "ech.analytics.selectors.AnalyticsCacheService.get_or_set",
        side_effect=passthrough_get_or_set,
    )
    def test_get_analytics_snapshot_by_id_returns_matching_snapshot(
        self,
        mock_get_or_set,
        mock_get_version,
    ):
        result = get_analytics_snapshot_by_id(snapshot_id=self.snapshot.id)

        self.assertEqual(result, self.snapshot)
        self.assertEqual(result.generated_by, self.snapshot.generated_by)
        self.assertIsNotNone(result.lifecycle)
        self.assertEqual(result.events.count(), 1)
        self.assertTrue(mock_get_or_set.called)
        self.assertTrue(mock_get_version.called)

    @patch(
        "ech.analytics.selectors.AnalyticsCacheService.get_snapshot_version",
        return_value=1,
    )
    @patch(
        "ech.analytics.selectors.AnalyticsCacheService.get_or_set",
        side_effect=passthrough_get_or_set,
    )
    def test_get_analytics_snapshot_by_id_raises_not_found_for_unknown_snapshot(
        self,
        mock_get_or_set,
        mock_get_version,
    ):
        with self.assertRaises(AnalyticsSnapshotNotFoundException):
            get_analytics_snapshot_by_id(snapshot_id=uuid.uuid4())

    @patch(
        "ech.analytics.selectors.AnalyticsCacheService.get_snapshot_version",
        return_value=1,
    )
    @patch(
        "ech.analytics.selectors.AnalyticsCacheService.get_or_set",
        side_effect=passthrough_get_or_set,
    )
    def test_get_analytics_snapshot_with_related_returns_matching_snapshot(
        self,
        mock_get_or_set,
        mock_get_version,
    ):
        result = get_analytics_snapshot_with_related(snapshot_id=self.snapshot.id)

        self.assertEqual(result, self.snapshot)
        self.assertIsNotNone(result.lifecycle)
        self.assertEqual(result.events.count(), 1)

    @patch(
        "ech.analytics.selectors.AnalyticsCacheService.get_snapshot_period_version",
        return_value=1,
    )
    @patch(
        "ech.analytics.selectors.AnalyticsCacheService.get_or_set",
        side_effect=passthrough_get_or_set,
    )
    def test_get_latest_analytics_snapshot_by_period_type_returns_latest_snapshot(
        self,
        mock_get_or_set,
        mock_get_period_version,
    ):
        now = timezone.now()

        older_snapshot = self.create_snapshot(
            period_type=AnalyticsSnapshot.PERIOD_WEEKLY,
            period_start=now - timedelta(days=14),
            period_end=now - timedelta(days=7),
        )
        latest_snapshot = self.create_snapshot(
            period_type=AnalyticsSnapshot.PERIOD_WEEKLY,
            period_start=now - timedelta(days=7),
            period_end=now,
        )

        result = get_latest_analytics_snapshot_by_period_type(
            period_type=AnalyticsSnapshot.PERIOD_WEEKLY,
        )

        self.assertEqual(result, latest_snapshot)
        self.assertNotEqual(result, older_snapshot)

    @patch(
        "ech.analytics.selectors.AnalyticsCacheService.get_snapshot_period_version",
        return_value=1,
    )
    @patch(
        "ech.analytics.selectors.AnalyticsCacheService.get_or_set",
        side_effect=passthrough_get_or_set,
    )
    def test_get_latest_analytics_snapshot_by_period_type_raises_not_found_when_empty(
        self,
        mock_get_or_set,
        mock_get_period_version,
    ):
        with self.assertRaises(AnalyticsSnapshotNotFoundException):
            get_latest_analytics_snapshot_by_period_type(
                period_type=AnalyticsSnapshot.PERIOD_MONTHLY,
            )


class AnalyticsSnapshotListSelectorTestCase(
    BaseAnalyticsSelectorFactoryMixin,
    TestCase,
):
    @classmethod
    def setUpTestData(cls):
        cls.generated_by = cls.create_staff_user()
        now = timezone.now()

        cls.snapshot_daily_old = cls.create_snapshot(
            generated_by=cls.generated_by,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=now - timedelta(days=3),
            period_end=now - timedelta(days=2),
            metadata={"tag": "old-daily"},
        )
        cls.snapshot_daily_new = cls.create_snapshot(
            generated_by=cls.generated_by,
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=now - timedelta(days=2),
            period_end=now - timedelta(days=1),
            metadata={"tag": "new-daily"},
        )
        cls.snapshot_weekly = cls.create_snapshot(
            generated_by=cls.generated_by,
            period_type=AnalyticsSnapshot.PERIOD_WEEKLY,
            period_start=now - timedelta(days=8),
            period_end=now - timedelta(days=1),
            metadata={"tag": "weekly-analytics"},
        )

    @patch(
        "ech.analytics.selectors.AnalyticsCacheService.get_management_version",
        return_value=1,
    )
    @patch(
        "ech.analytics.selectors.AnalyticsCacheService.get_or_set",
        side_effect=passthrough_get_or_set,
    )
    def test_list_analytics_snapshots_returns_all_snapshots(
        self,
        mock_get_or_set,
        mock_get_management_version,
    ):
        result = list_analytics_snapshots()

        self.assertEqual(result.count(), 3)
        self.assertEqual(
            list(result),
            [self.snapshot_weekly, self.snapshot_daily_new, self.snapshot_daily_old],
        )

    @patch(
        "ech.analytics.selectors.AnalyticsCacheService.get_snapshot_period_version",
        return_value=1,
    )
    @patch(
        "ech.analytics.selectors.AnalyticsCacheService.get_or_set",
        side_effect=passthrough_get_or_set,
    )
    def test_list_analytics_snapshots_by_period_type_filters_results(
        self,
        mock_get_or_set,
        mock_get_period_version,
    ):
        result = list_analytics_snapshots_by_period_type(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
        )

        self.assertEqual(result.count(), 2)
        self.assertEqual(
            list(result),
            [self.snapshot_daily_new, self.snapshot_daily_old],
        )

    @patch(
        "ech.analytics.selectors.AnalyticsCacheService.get_management_version",
        return_value=1,
    )
    @patch(
        "ech.analytics.selectors.AnalyticsCacheService.get_or_set",
        side_effect=passthrough_get_or_set,
    )
    def test_list_analytics_snapshots_by_period_range_filters_by_bounds(
        self,
        mock_get_or_set,
        mock_get_management_version,
    ):
        result = list_analytics_snapshots_by_period_range(
            period_start=self.snapshot_daily_old.period_start,
            period_end=self.snapshot_daily_new.period_end,
        )

        self.assertEqual(result.count(), 2)
        self.assertEqual(
            list(result),
            [self.snapshot_daily_new, self.snapshot_daily_old],
        )

    @patch(
        "ech.analytics.selectors.AnalyticsCacheService.get_management_version",
        return_value=1,
    )
    @patch(
        "ech.analytics.selectors.AnalyticsCacheService.get_or_set",
        side_effect=passthrough_get_or_set,
    )
    def test_list_analytics_snapshots_by_period_range_with_period_type_filters_fully(
        self,
        mock_get_or_set,
        mock_get_management_version,
    ):
        result = list_analytics_snapshots_by_period_range(
            period_start=self.snapshot_weekly.period_start,
            period_end=self.snapshot_weekly.period_end,
            period_type=AnalyticsSnapshot.PERIOD_WEEKLY,
        )

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.snapshot_weekly)

    def test_list_recent_analytics_snapshots_returns_ordered_queryset(self):
        result = list_recent_analytics_snapshots()

        self.assertEqual(
            list(result),
            [self.snapshot_weekly, self.snapshot_daily_new, self.snapshot_daily_old],
        )

    @patch(
        "ech.analytics.selectors.AnalyticsCacheService.get_management_version",
        return_value=1,
    )
    @patch(
        "ech.analytics.selectors.AnalyticsCacheService.get_or_set",
        side_effect=passthrough_get_or_set,
    )
    def test_search_analytics_snapshots_matches_period_type(
        self,
        mock_get_or_set,
        mock_get_management_version,
    ):
        result = search_analytics_snapshots(query="daily")

        self.assertEqual(result.count(), 2)
        self.assertEqual(
            list(result),
            [self.snapshot_daily_new, self.snapshot_daily_old],
        )

    @patch(
        "ech.analytics.selectors.AnalyticsCacheService.get_management_version",
        return_value=1,
    )
    @patch(
        "ech.analytics.selectors.AnalyticsCacheService.get_or_set",
        side_effect=passthrough_get_or_set,
    )
    def test_search_analytics_snapshots_matches_metadata_content(
        self,
        mock_get_or_set,
        mock_get_management_version,
    ):
        result = search_analytics_snapshots(query="weekly-analytics")

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.snapshot_weekly)


class AnalyticsOperationalBaseQuerysetTestCase(
    BaseAnalyticsSelectorFactoryMixin,
    TestCase,
):
    def test_order_analytics_base_queryset_applies_related_loading(self):
        queryset = order_analytics_base_queryset()

        self.assertEqual(
            queryset.query.select_related,
            {
                "customer": {},
                "totals": {},
                "lifecycle": {},
                "address": {},
            },
        )
        self.assertEqual(
            set(queryset._prefetch_related_lookups),
            {"items", "events"},
        )

    def test_payment_analytics_base_queryset_applies_related_loading(self):
        queryset = payment_analytics_base_queryset()

        self.assertEqual(
            queryset.query.select_related,
            {
                "order": {},
                "customer": {},
                "lifecycle": {},
            },
        )
        self.assertEqual(
            set(queryset._prefetch_related_lookups),
            {"transactions", "refunds", "events"},
        )

    def test_shipment_analytics_base_queryset_applies_related_loading(self):
        queryset = shipment_analytics_base_queryset()

        self.assertEqual(
            queryset.query.select_related,
            {
                "order": {},
                "customer": {},
                "address": {},
                "lifecycle": {},
            },
        )
        self.assertEqual(
            set(queryset._prefetch_related_lookups),
            {"events", "tracking_updates", "notes"},
        )

    def test_product_analytics_base_queryset_applies_related_loading(self):
        queryset = product_analytics_base_queryset()

        self.assertEqual(
            queryset.query.select_related,
            {
                "sold_by": {},
                "inventory_record": {},
            },
        )
        self.assertEqual(
            set(queryset._prefetch_related_lookups),
            {"images", "reviews", "event_logs"},
        )

    def test_review_analytics_base_queryset_applies_related_loading(self):
        queryset = review_analytics_base_queryset()

        self.assertEqual(
            queryset.query.select_related,
            {
                "customer": {},
                "product": {},
                "moderated_by": {},
                "lifecycle": {},
            },
        )
        self.assertEqual(
            set(queryset._prefetch_related_lookups),
            {"events"},
        )

    def test_notification_analytics_base_queryset_applies_related_loading(self):
        queryset = notification_analytics_base_queryset()

        self.assertEqual(
            queryset.query.select_related,
            {
                "recipient": {},
                "created_by": {},
                "lifecycle": {},
            },
        )
        self.assertEqual(
            set(queryset._prefetch_related_lookups),
            {"deliveries", "events"},
        )


class AnalyticsOperationalListSelectorTestCase(
    BaseAnalyticsSelectorFactoryMixin,
    TestCase,
):
    @classmethod
    def setUpTestData(cls):
        cls.period_start = timezone.now() - timedelta(days=2)
        cls.period_end = timezone.now() + timedelta(days=1)

        cls.customer = cls.create_user()
        cls.staff_user = cls.create_staff_user()

        cls.product = cls.create_product()
        cls.second_product = cls.create_product()

        cls.order_inside = cls.create_order_with_related_data(
            customer=cls.customer,
            product=cls.product,
            status=Order.ORDER_STATUS_DELIVERED,
        )
        cls.order_outside = cls.create_order_with_related_data(
            customer=cls.customer,
            product=cls.product,
            status=Order.ORDER_STATUS_PENDING,
        )
        Order.objects.filter(id=cls.order_inside.id).update(
            created_at=timezone.now() - timedelta(hours=12),
        )
        Order.objects.filter(id=cls.order_outside.id).update(
            created_at=timezone.now() - timedelta(days=10),
        )

        cls.payment_inside = cls.create_payment_with_related_data(
            order=cls.order_inside,
            customer=cls.customer,
            status=Payment.PAYMENT_STATUS_CAPTURED,
        )
        cls.payment_outside = cls.create_payment_with_related_data(
            order=cls.order_outside,
            customer=cls.customer,
            status=Payment.PAYMENT_STATUS_FAILED,
        )
        Payment.objects.filter(id=cls.payment_inside.id).update(
            created_at=timezone.now() - timedelta(hours=10),
        )
        Payment.objects.filter(id=cls.payment_outside.id).update(
            created_at=timezone.now() - timedelta(days=10),
        )

        cls.shipment_inside = cls.create_shipment_with_related_data(
            order=cls.order_inside,
            customer=cls.customer,
            status=Shipment.STATUS_DELIVERED,
        )
        cls.shipment_outside = cls.create_shipment_with_related_data(
            order=cls.order_outside,
            customer=cls.customer,
            status=Shipment.STATUS_PENDING,
        )
        Shipment.objects.filter(id=cls.shipment_inside.id).update(
            created_at=timezone.now() - timedelta(hours=8),
        )
        Shipment.objects.filter(id=cls.shipment_outside.id).update(
            created_at=timezone.now() - timedelta(days=10),
        )

        cls.review_inside = cls.create_review_with_related_data(
            customer=cls.customer,
            product=cls.product,
            status=Review.REVIEW_STATUS_APPROVED,
        )
        cls.review_outside_customer = cls.create_user()
        cls.review_outside = cls.create_review_with_related_data(
            customer=cls.review_outside_customer,
            product=cls.second_product,
            status=Review.REVIEW_STATUS_REJECTED,
        )
        Review.objects.filter(id=cls.review_inside.id).update(
            created_at=timezone.now() - timedelta(hours=6),
        )
        Review.objects.filter(id=cls.review_outside.id).update(
            created_at=timezone.now() - timedelta(days=10),
        )

        cls.notification_inside = cls.create_notification_with_related_data(
            recipient=cls.customer,
            created_by=cls.staff_user,
        )
        cls.notification_outside = cls.create_notification_with_related_data(
            recipient=cls.customer,
            created_by=cls.staff_user,
        )
        Notification.objects.filter(id=cls.notification_inside.id).update(
            created_at=timezone.now() - timedelta(hours=4),
        )
        Notification.objects.filter(id=cls.notification_outside.id).update(
            created_at=timezone.now() - timedelta(days=10),
        )

        cls.customer_inside = cls.create_user(
            email=f"customer_in_{cls.unique_suffix()}@test.com",
        )
        cls.customer_outside = cls.create_user(
            email=f"customer_out_{cls.unique_suffix()}@test.com",
        )
        User.objects.filter(id=cls.customer_inside.id).update(
            date_joined=timezone.now() - timedelta(hours=3),
        )
        User.objects.filter(id=cls.customer_outside.id).update(
            date_joined=timezone.now() - timedelta(days=10),
        )

        cls.staff_inside = cls.create_staff_user(
            email=f"analytics_{cls.unique_suffix()}@company.com",
        )
        cls.staff_outside = cls.create_staff_user(
            email=f"admin_{cls.unique_suffix()}@company.com",
        )
        User.objects.filter(id=cls.staff_inside.id).update(
            date_joined=timezone.now() - timedelta(hours=2),
        )
        User.objects.filter(id=cls.staff_outside.id).update(
            date_joined=timezone.now() - timedelta(days=20),
        )

    def test_list_orders_for_analytics_filters_by_created_at(self):
        result = list_orders_for_analytics(
            period_start=self.period_start,
            period_end=self.period_end,
        )

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.order_inside)
        self.assertEqual(result.first().items.count(), 1)
        self.assertEqual(result.first().events.count(), 1)

    def test_list_payments_for_analytics_filters_by_created_at(self):
        result = list_payments_for_analytics(
            period_start=self.period_start,
            period_end=self.period_end,
        )

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.payment_inside)
        self.assertEqual(result.first().transactions.count(), 1)
        self.assertEqual(result.first().refunds.count(), 1)

    def test_list_shipments_for_analytics_filters_by_created_at(self):
        result = list_shipments_for_analytics(
            period_start=self.period_start,
            period_end=self.period_end,
        )

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.shipment_inside)
        self.assertEqual(result.first().tracking_updates.count(), 1)
        self.assertEqual(result.first().notes.count(), 1)

    def test_list_products_for_analytics_returns_all_products(self):
        result = list_products_for_analytics()

        self.assertIn(self.product, result)
        self.assertIn(self.second_product, result)
        self.assertEqual(result.count(), 2)

    def test_customer_analytics_base_queryset_returns_only_customer_users(self):
        result = customer_analytics_base_queryset()

        self.assertIn(self.customer, result)
        self.assertIn(self.customer_inside, result)
        self.assertNotIn(self.staff_user, result)
        self.assertNotIn(self.staff_inside, result)

    def test_list_customers_for_analytics_without_bounds_returns_all_customers(self):
        result = list_customers_for_analytics()

        self.assertIn(self.customer, result)
        self.assertIn(self.customer_inside, result)
        self.assertIn(self.customer_outside, result)
        self.assertNotIn(self.staff_user, result)

    def test_list_customers_for_analytics_filters_by_join_date_range(self):
        result = list_customers_for_analytics(
            period_start=self.period_start,
            period_end=self.period_end,
        )

        self.assertIn(self.customer, result)
        self.assertIn(self.customer_inside, result)
        self.assertNotIn(self.customer_outside, result)
        self.assertNotIn(self.staff_user, result)
        self.assertNotIn(self.staff_inside, result)

    def test_user_analytics_base_queryset_returns_all_users(self):
        result = user_analytics_base_queryset()

        self.assertIn(self.customer, result)
        self.assertIn(self.staff_user, result)
        self.assertIn(self.staff_inside, result)

    def test_list_users_for_analytics_filters_by_period_end(self):
        result = list_users_for_analytics(
            period_end=self.period_end,
        )

        self.assertIn(self.customer_inside, result)
        self.assertIn(self.staff_inside, result)
        self.assertIn(self.customer_outside, result)

    def test_list_reviews_for_analytics_filters_by_created_at(self):
        result = list_reviews_for_analytics(
            period_start=self.period_start,
            period_end=self.period_end,
        )

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.review_inside)
        self.assertEqual(result.first().events.count(), 1)

    def test_list_notifications_for_analytics_filters_by_created_at(self):
        result = list_notifications_for_analytics(
            period_start=self.period_start,
            period_end=self.period_end,
        )

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.notification_inside)
        self.assertEqual(result.first().deliveries.count(), 1)
        self.assertEqual(result.first().events.count(), 1)