import uuid
from decimal import Decimal

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from ech.admin_dashboard.models import AdminDashboardLog
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
from ech.users.models import CustomUser


class AdminDashboardCacheSelectorsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = CustomUser.objects.create_user(
            email="admin.dashboard@company.com",
            password="StrongPassword123",
            user_name="Admin Dashboard Staff",
            role=CustomUser.ROLE_ADMIN,
            is_active=True,
            email_confirmed=True,
        )

        cls.customer = CustomUser.objects.create_user(
            email="customer.dashboard@test.com",
            password="StrongPassword123",
            user_name="Customer Dashboard User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        cls.product = cls.create_product_with_related(
            sold_by=cls.staff,
            is_active=True,
            quantity=10,
        )

        cls.order = cls.create_order_with_related(
            customer=cls.customer,
            product=cls.product,
            status=Order.ORDER_STATUS_PENDING,
        )

        cls.payment = cls.create_payment_with_related(
            order=cls.order,
            customer=cls.customer,
            status=Payment.PAYMENT_STATUS_CAPTURED,
        )

        cls.shipment_order = cls.create_order_with_related(
            customer=cls.customer,
            product=cls.product,
            status=Order.ORDER_STATUS_CONFIRMED,
        )
        cls.shipment = cls.create_shipment_with_related(
            order=cls.shipment_order,
            customer=cls.customer,
            status=Shipment.STATUS_IN_TRANSIT,
        )

        cls.review = cls.create_review_with_related(
            customer=cls.customer,
            product=cls.product,
            status=Review.REVIEW_STATUS_APPROVED,
        )

        cls.notification = cls.create_notification_with_related(
            recipient=cls.customer,
            created_by=cls.staff,
            status=Notification.STATUS_UNREAD,
        )

        cls.admin_log = AdminDashboardLog.objects.create(
            action_type="bulk_review_moderation",
            performed_by=cls.staff,
            target_module="reviews",
            metadata={"source": "cache-test"},
        )

    def setUp(self):
        cache.clear()

    @classmethod
    def unique_suffix(cls):
        return uuid.uuid4().hex[:8]

    @classmethod
    def create_product_with_related(
        cls,
        *,
        sold_by,
        is_active=True,
        quantity=10,
    ):
        product = Product.objects.create(
            name=f"Product {cls.unique_suffix()}",
            product_type=Product.PHONE,
            brand="Apple",
            sold_by=sold_by,
            description="Product description",
            technical_information="Specs",
            price=Decimal("5000.00"),
            discount_price=Decimal("4500.00"),
            is_active=is_active,
        )

        ProductInventory.objects.create(
            product=product,
            quantity=quantity,
        )
        ProductEventLog.objects.create(
            product=product,
            event_type=ProductEventLog.EVENT_PRODUCT_CREATED,
        )

        return product

    @classmethod
    def create_order_with_related(
        cls,
        *,
        customer,
        product,
        status,
    ):
        order = Order.objects.create(
            customer=customer,
            status=status,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
            currency="USD",
        )

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
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name_snapshot=product.name,
            product_type_snapshot=product.product_type,
            brand_snapshot=product.brand,
            quantity=1,
            unit_price=Decimal("5000.00"),
            discount_price=Decimal("4500.00"),
            total_price=Decimal("4500.00"),
        )

        return order

    @classmethod
    def create_payment_with_related(
        cls,
        *,
        order,
        customer,
        status,
    ):
        payment = Payment.objects.create(
            order=order,
            customer=customer,
            payment_reference=f"PAY-{cls.unique_suffix().upper()}",
            method=Payment.PAYMENT_METHOD_PIX,
            status=status,
            amount=Decimal("4500.00"),
            refunded_amount=Decimal("0.00"),
            currency="USD",
            gateway_name="stripe",
            gateway_payment_id=f"GW-{cls.unique_suffix()}",
            gateway_customer_id=f"CUST-{cls.unique_suffix()}",
            metadata={"source": "cache-test"},
        )

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
    def create_shipment_with_related(
        cls,
        *,
        order,
        customer,
        status,
    ):
        shipment = Shipment.objects.create(
            order=order,
            customer=customer,
            status=status,
            shipping_method=Shipment.METHOD_STANDARD,
            carrier_name="DHL",
            tracking_code=f"TRACK-{cls.unique_suffix().upper()}",
            external_reference=f"EXT-{cls.unique_suffix().upper()}",
            shipping_cost=Decimal("25.00"),
            currency="USD",
            estimated_delivery_date=timezone.now().date(),
        )

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
        ShipmentLifecycle.objects.create(shipment=shipment)
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
            author=customer,
            message="Operational note",
            is_internal=True,
        )

        return shipment

    @classmethod
    def create_review_with_related(
        cls,
        *,
        customer,
        product,
        status,
    ):
        review = Review.objects.create(
            customer=customer,
            product=product,
            rating=5,
            title="Excellent",
            comment="Very good product",
            status=status,
            is_verified_purchase=True,
        )

        ReviewLifecycle.objects.create(review=review)
        ReviewEvent.objects.create(
            review=review,
            event_type=ReviewEvent.TYPE_CREATED,
        )

        return review

    @classmethod
    def create_notification_with_related(
        cls,
        *,
        recipient,
        created_by,
        status,
    ):
        notification = Notification.objects.create(
            recipient=recipient,
            created_by=created_by,
            notification_type="order_shipped",
            title="Order update",
            message="Your order has been updated.",
            status=status,
            channel=Notification.CHANNEL_IN_APP,
            priority=Notification.PRIORITY_NORMAL,
            source_module="orders",
            source_event="order_shipped",
            source_object_id=str(uuid.uuid4()),
            metadata={"source": "cache-test"},
        )

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

    def test_admin_dashboard_summary_service_uses_cached_summary_payload(self):
        """Return cached dashboard summary until cache is invalidated."""
        summary = AdminDashboardSummaryService.get_summary(
            performed_by=self.staff,
        )
        self.assertEqual(summary["orders"]["total_orders"], 2)
        self.assertEqual(summary["products"]["total_products"], 1)

        second_product = self.create_product_with_related(
            sold_by=self.staff,
            is_active=True,
            quantity=20,
        )
        self.create_order_with_related(
            customer=self.customer,
            product=second_product,
            status=Order.ORDER_STATUS_DELIVERED,
        )

        cached_summary = AdminDashboardSummaryService.get_summary(
            performed_by=self.staff,
        )
        self.assertEqual(cached_summary["orders"]["total_orders"], 2)
        self.assertEqual(cached_summary["products"]["total_products"], 1)

    def test_admin_dashboard_operational_metrics_service_uses_cached_payload(self):
        """Return cached operational metrics until cache is invalidated."""
        metrics = AdminDashboardOperationalMetricsService.get_operational_metrics(
            performed_by=self.staff,
        )
        self.assertEqual(metrics["orders"]["pending_orders"], 1)
        self.assertEqual(metrics["notifications"]["failed_notifications"], 0)

        failed_notification = self.create_notification_with_related(
            recipient=self.customer,
            created_by=self.staff,
            status=Notification.STATUS_FAILED,
        )
        self.assertIsNotNone(failed_notification)

        cached_metrics = (
            AdminDashboardOperationalMetricsService.get_operational_metrics(
                performed_by=self.staff,
            )
        )
        self.assertEqual(cached_metrics["orders"]["pending_orders"], 1)
        self.assertEqual(cached_metrics["notifications"]["failed_notifications"], 0)

    def test_admin_dashboard_recent_activity_service_uses_cached_payload(self):
        """Return cached recent activity until cache is invalidated."""
        activity = AdminDashboardRecentActivityService.get_recent_activity(
            limit=20,
            performed_by=self.staff,
        )
        self.assertEqual(activity["total"], 8)

        extra_product = self.create_product_with_related(
            sold_by=self.staff,
            is_active=True,
            quantity=5,
        )
        self.assertIsNotNone(extra_product)

        cached_activity = AdminDashboardRecentActivityService.get_recent_activity(
            limit=20,
            performed_by=self.staff,
        )
        self.assertEqual(cached_activity["total"], 8)

    def test_admin_dashboard_recent_activity_service_uses_distinct_cache_per_limit(self):
        """Use distinct cache entries for different recent activity limits."""
        first_payload = AdminDashboardRecentActivityService.get_recent_activity(
            limit=2,
            performed_by=self.staff,
        )
        second_payload = AdminDashboardRecentActivityService.get_recent_activity(
            limit=5,
            performed_by=self.staff,
        )

        self.assertEqual(first_payload["limit"], 2)
        self.assertEqual(first_payload["total"], 2)
        self.assertEqual(len(first_payload["activities"]), 2)

        self.assertEqual(second_payload["limit"], 5)
        self.assertEqual(second_payload["total"], 5)
        self.assertEqual(len(second_payload["activities"]), 5)

    def test_admin_dashboard_alerts_service_uses_cached_alert_payload(self):
        """Return cached alerts until cache is invalidated."""
        alerts_payload = AdminDashboardAlertsService.get_alerts(
            performed_by=self.staff,
        )
        self.assertEqual(alerts_payload["total_alerts"], 2)

        alert_types = {alert["type"] for alert in alerts_payload["alerts"]}
        self.assertIn("pending_orders", alert_types)
        self.assertIn("products_without_images", alert_types)

        failed_payment_order = self.create_order_with_related(
            customer=self.customer,
            product=self.product,
            status=Order.ORDER_STATUS_CONFIRMED,
        )
        self.create_payment_with_related(
            order=failed_payment_order,
            customer=self.customer,
            status=Payment.PAYMENT_STATUS_FAILED,
        )

        cached_alerts_payload = AdminDashboardAlertsService.get_alerts(
            performed_by=self.staff,
        )
        self.assertEqual(cached_alerts_payload["total_alerts"], 2)

        cached_alert_types = {
            alert["type"] for alert in cached_alerts_payload["alerts"]
        }
        self.assertIn("pending_orders", cached_alert_types)
        self.assertIn("products_without_images", cached_alert_types)