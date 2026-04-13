import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ech.admin_dashboard.models import (
    AdminDashboardEvent,
    AdminDashboardLog,
)
from ech.admin_dashboard.selectors import (
    admin_dashboard_event_base_queryset,
    admin_dashboard_log_base_queryset,
    order_admin_base_queryset,
    payment_admin_base_queryset,
    shipment_admin_base_queryset,
    review_admin_base_queryset,
    notification_admin_base_queryset,
    product_admin_base_queryset,
    get_orders_summary_metrics,
    get_payments_summary_metrics,
    get_shipping_summary_metrics,
    get_users_summary_metrics,
    get_reviews_summary_metrics,
    get_products_summary_metrics,
    get_order_operational_metrics,
    get_payment_operational_metrics,
    get_shipping_operational_metrics,
    get_review_operational_metrics,
    get_notification_operational_metrics,
    get_product_operational_metrics,
    get_recent_order_activity,
    get_recent_payment_activity,
    get_recent_shipping_activity,
    get_recent_review_activity,
    get_recent_notification_activity,
    get_recent_admin_activity,
    get_recent_product_activity,
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

User = get_user_model()


class BaseAdminDashboardSelectorFactoryMixin:
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
            "role": User.ROLE_ADMIN,
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
            "estimated_delivery_date": timezone.now().date(),
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
    def create_admin_log(cls, **kwargs):
        performed_by = kwargs.pop("performed_by", None) or cls.create_staff_user()

        data = {
            "action_type": "bulk_review_moderation",
            "performed_by": performed_by,
            "target_module": "reviews",
            "metadata": {"source": "test"},
        }
        data.update(kwargs)
        return AdminDashboardLog.objects.create(**data)

    @classmethod
    def create_admin_event(cls, **kwargs):
        performed_by = kwargs.pop("performed_by", None) or cls.create_staff_user()
        related_log = kwargs.pop("related_log", None)

        data = {
            "event_type": AdminDashboardEvent.TYPE_DASHBOARD_VIEWED,
            "performed_by": performed_by,
            "related_log": related_log,
            "metadata": {"source": "test"},
        }
        data.update(kwargs)
        return AdminDashboardEvent.objects.create(**data)


class AdminDashboardBaseQuerysetSelectorTestCase(
    BaseAdminDashboardSelectorFactoryMixin,
    TestCase,
):
    def test_admin_dashboard_event_base_queryset_applies_select_related(self):
        """Ensure the admin dashboard event base queryset eagerly loads performed_by and related_log."""
        queryset = admin_dashboard_event_base_queryset()

        self.assertEqual(
            queryset.query.select_related,
            {
                "performed_by": {},
                "related_log": {},
            },
        )

    def test_admin_dashboard_log_base_queryset_applies_select_related(self):
        """Ensure the admin dashboard log base queryset eagerly loads performed_by."""
        queryset = admin_dashboard_log_base_queryset()

        self.assertEqual(
            queryset.query.select_related,
            {
                "performed_by": {},
            },
        )

    def test_order_admin_base_queryset_applies_related_loading(self):
        """Ensure the order admin queryset applies the expected select_related and prefetch_related configuration."""
        queryset = order_admin_base_queryset()

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

    def test_payment_admin_base_queryset_applies_related_loading(self):
        """Ensure the payment admin queryset applies the expected related object loading strategy."""
        queryset = payment_admin_base_queryset()

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

    def test_shipment_admin_base_queryset_applies_related_loading(self):
        """Ensure the shipment admin queryset applies the expected related object loading strategy."""
        queryset = shipment_admin_base_queryset()

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

    def test_review_admin_base_queryset_applies_related_loading(self):
        """Ensure the review admin queryset applies the expected related object loading strategy."""
        queryset = review_admin_base_queryset()

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

    def test_notification_admin_base_queryset_applies_related_loading(self):
        """Ensure the notification admin queryset applies the expected related object loading strategy."""
        queryset = notification_admin_base_queryset()

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

    def test_product_admin_base_queryset_applies_related_loading(self):
        """Ensure the product admin queryset applies the expected related object loading strategy."""
        queryset = product_admin_base_queryset()

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


class AdminDashboardSummaryMetricsSelectorTestCase(
    BaseAdminDashboardSelectorFactoryMixin,
    TestCase,
):
    @classmethod
    def setUpTestData(cls):
        cls.customer = cls.create_user()
        cls.staff_user = cls.create_staff_user()

        cls.product_active = cls.create_product_with_related_data(is_active=True)
        cls.product_inactive = cls.create_product_with_related_data(
            is_active=False,
            name="Inactive product",
        )

        cls.order_pending = cls.create_order_with_related_data(
            customer=cls.customer,
            product=cls.product_active,
            status=Order.ORDER_STATUS_PENDING,
        )
        cls.order_processing = cls.create_order_with_related_data(
            customer=cls.customer,
            product=cls.product_active,
            status=Order.ORDER_STATUS_PROCESSING,
        )
        cls.order_shipped = cls.create_order_with_related_data(
            customer=cls.customer,
            product=cls.product_active,
            status=Order.ORDER_STATUS_SHIPPED,
        )
        cls.order_delivered = cls.create_order_with_related_data(
            customer=cls.customer,
            product=cls.product_active,
            status=Order.ORDER_STATUS_DELIVERED,
        )
        cls.order_cancelled = cls.create_order_with_related_data(
            customer=cls.customer,
            product=cls.product_active,
            status=Order.ORDER_STATUS_CANCELLED,
        )

        cls.payment_captured = cls.create_payment_with_related_data(
            order=cls.order_pending,
            customer=cls.customer,
            status=Payment.PAYMENT_STATUS_CAPTURED,
        )
        cls.payment_failed = cls.create_payment_with_related_data(
            order=cls.order_processing,
            customer=cls.customer,
            status=Payment.PAYMENT_STATUS_FAILED,
        )
        cls.payment_refunded = cls.create_payment_with_related_data(
            order=cls.order_shipped,
            customer=cls.customer,
            status=Payment.PAYMENT_STATUS_REFUNDED,
        )
        cls.payment_partially_refunded = cls.create_payment_with_related_data(
            order=cls.order_delivered,
            customer=cls.customer,
            status=Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED,
        )

        cls.shipment_pending = cls.create_shipment_with_related_data(
            order=cls.order_cancelled,
            customer=cls.customer,
            status=Shipment.STATUS_PENDING,
        )
        cls.shipment_in_transit_order = cls.create_order_with_related_data(
            customer=cls.create_user(),
            product=cls.product_active,
            status=Order.ORDER_STATUS_CONFIRMED,
        )
        cls.shipment_in_transit = cls.create_shipment_with_related_data(
            customer=cls.shipment_in_transit_order.customer,
            order=cls.shipment_in_transit_order,
            status=Shipment.STATUS_IN_TRANSIT,
        )
        cls.shipment_delivered_order = cls.create_order_with_related_data(
            customer=cls.create_user(),
            product=cls.product_active,
            status=Order.ORDER_STATUS_DELIVERED,
        )
        cls.shipment_delivered = cls.create_shipment_with_related_data(
            customer=cls.shipment_delivered_order.customer,
            order=cls.shipment_delivered_order,
            status=Shipment.STATUS_DELIVERED,
        )
        cls.shipment_failed_order = cls.create_order_with_related_data(
            customer=cls.create_user(),
            product=cls.product_active,
            status=Order.ORDER_STATUS_PROCESSING,
        )
        cls.shipment_failed = cls.create_shipment_with_related_data(
            customer=cls.shipment_failed_order.customer,
            order=cls.shipment_failed_order,
            status=Shipment.STATUS_FAILED,
        )
        cls.shipment_returned_order = cls.create_order_with_related_data(
            customer=cls.create_user(),
            product=cls.product_active,
            status=Order.ORDER_STATUS_CANCELLED,
        )
        cls.shipment_returned = cls.create_shipment_with_related_data(
            customer=cls.shipment_returned_order.customer,
            order=cls.shipment_returned_order,
            status=Shipment.STATUS_RETURNED,
        )

        cls.review_pending = cls.create_review_with_related_data(
            customer=cls.customer,
            product=cls.product_active,
            status=Review.REVIEW_STATUS_PENDING,
        )
        cls.review_approved = cls.create_review_with_related_data(
            customer=cls.create_user(),
            product=cls.product_inactive,
            status=Review.REVIEW_STATUS_APPROVED,
        )
        cls.review_rejected = cls.create_review_with_related_data(
            customer=cls.create_user(),
            product=cls.product_active,
            status=Review.REVIEW_STATUS_REJECTED,
        )
        cls.review_hidden = cls.create_review_with_related_data(
            customer=cls.create_user(),
            product=cls.product_inactive,
            status=Review.REVIEW_STATUS_HIDDEN,
        )
        cls.review_cancelled = cls.create_review_with_related_data(
            customer=cls.create_user(),
            product=cls.product_active,
            status=Review.REVIEW_STATUS_CANCELLED,
        )

    def test_get_orders_summary_metrics_returns_expected_counts(self):
        """Ensure order summary metrics return the expected totals for each tracked order status."""
        result = get_orders_summary_metrics()

        self.assertEqual(result["total_orders"], 9)
        self.assertEqual(result["pending_orders"], 1)
        self.assertEqual(result["processing_orders"], 2)
        self.assertEqual(result["shipped_orders"], 1)
        self.assertEqual(result["delivered_orders"], 2)
        self.assertEqual(result["cancelled_orders"], 2)

    def test_get_payments_summary_metrics_returns_expected_counts(self):
        """Ensure payment summary metrics return the expected totals for each tracked payment status."""
        result = get_payments_summary_metrics()

        self.assertEqual(result["total_payments"], 4)
        self.assertEqual(result["captured_payments"], 1)
        self.assertEqual(result["failed_payments"], 1)
        self.assertEqual(result["refunded_payments"], 1)
        self.assertEqual(result["partially_refunded_payments"], 1)

    def test_get_shipping_summary_metrics_returns_expected_counts(self):
        """Ensure shipping summary metrics return the expected totals for each tracked shipment status."""
        result = get_shipping_summary_metrics()

        self.assertEqual(result["total_shipments"], 5)
        self.assertEqual(result["pending_shipments"], 1)
        self.assertEqual(result["in_transit_shipments"], 1)
        self.assertEqual(result["delivered_shipments"], 1)
        self.assertEqual(result["failed_shipments"], 1)
        self.assertEqual(result["returned_shipments"], 1)

    def test_get_users_summary_metrics_returns_expected_counts(self):
        """Ensure user summary metrics reflect the current totals for activity, role, and email confirmation state."""
        inactive_customer = self.create_user(
            email=f"inactive_{self.unique_suffix()}@test.com",
            is_active=False,
            email_confirmed=False,
        )

        result = get_users_summary_metrics()

        self.assertEqual(result["total_users"], User.objects.count())
        self.assertEqual(
            result["active_users"],
            User.objects.filter(is_active=True).count(),
        )
        self.assertEqual(
            result["inactive_users"],
            User.objects.filter(is_active=False).count(),
        )
        self.assertEqual(
            result["staff_users"],
            User.objects.exclude(user_role=User.ROLE_CUSTOMER_USER).count(),
        )
        self.assertEqual(
            result["customer_users"],
            User.objects.filter(user_role=User.ROLE_CUSTOMER_USER).count(),
        )
        self.assertEqual(
            result["confirmed_users"],
            User.objects.filter(email_confirmed=True).count(),
        )
        self.assertEqual(
            result["unconfirmed_users"],
            User.objects.filter(email_confirmed=False).count(),
        )
        self.assertIsNotNone(inactive_customer)

    def test_get_reviews_summary_metrics_returns_expected_counts(self):
        """Ensure review summary metrics return the expected totals for each tracked review moderation state."""
        result = get_reviews_summary_metrics()

        self.assertEqual(result["total_reviews"], 5)
        self.assertEqual(result["pending_reviews"], 1)
        self.assertEqual(result["approved_reviews"], 1)
        self.assertEqual(result["rejected_reviews"], 1)
        self.assertEqual(result["hidden_reviews"], 1)
        self.assertEqual(result["cancelled_reviews"], 1)

    def test_get_products_summary_metrics_returns_expected_counts(self):
        """Ensure product summary metrics return the expected totals for active and inactive products."""
        result = get_products_summary_metrics()

        self.assertEqual(result["total_products"], 2)
        self.assertEqual(result["active_products"], 1)
        self.assertEqual(result["inactive_products"], 1)


class AdminDashboardOperationalMetricsSelectorTestCase(
    BaseAdminDashboardSelectorFactoryMixin,
    TestCase,
):
    @classmethod
    def setUpTestData(cls):
        cls.customer = cls.create_user()
        cls.staff_user = cls.create_staff_user()

        cls.product_low_stock = cls.create_product_with_related_data(
            is_active=True,
            name="Low stock product",
        )
        cls.product_low_stock.inventory_record.quantity = 3
        cls.product_low_stock.inventory_record.save(update_fields=["quantity"])

        cls.product_out_of_stock = cls.create_product_with_related_data(
            is_active=True,
            name="Out of stock product",
        )
        cls.product_out_of_stock.inventory_record.quantity = 0
        cls.product_out_of_stock.inventory_record.save(update_fields=["quantity"])

        cls.product_without_images = cls.create_product(
            is_active=True,
            name="Without images product",
        )
        ProductInventory.objects.create(
            product=cls.product_without_images,
            quantity=7,
        )

        cls.create_order_with_related_data(
            customer=cls.customer,
            product=cls.product_low_stock,
            status=Order.ORDER_STATUS_PENDING,
        )
        cls.create_order_with_related_data(
            customer=cls.customer,
            product=cls.product_out_of_stock,
            status=Order.ORDER_STATUS_PROCESSING,
        )
        cls.create_order_with_related_data(
            customer=cls.customer,
            product=cls.product_without_images,
            status=Order.ORDER_STATUS_CANCELLED,
        )

        payment_order_failed = cls.create_order_with_related_data(
            customer=cls.customer,
            product=cls.product_low_stock,
            status=Order.ORDER_STATUS_CONFIRMED,
        )
        payment_order_processing = cls.create_order_with_related_data(
            customer=cls.customer,
            product=cls.product_out_of_stock,
            status=Order.ORDER_STATUS_CONFIRMED,
        )
        payment_order_refunded = cls.create_order_with_related_data(
            customer=cls.customer,
            product=cls.product_without_images,
            status=Order.ORDER_STATUS_CONFIRMED,
        )

        cls.create_payment_with_related_data(
            order=payment_order_failed,
            customer=cls.customer,
            status=Payment.PAYMENT_STATUS_FAILED,
        )
        cls.create_payment_with_related_data(
            order=payment_order_processing,
            customer=cls.customer,
            status=Payment.PAYMENT_STATUS_PROCESSING,
        )
        cls.create_payment_with_related_data(
            order=payment_order_refunded,
            customer=cls.customer,
            status=Payment.PAYMENT_STATUS_REFUNDED,
        )

        shipment_order_failed = cls.create_order_with_related_data(
            customer=cls.customer,
            product=cls.product_low_stock,
            status=Order.ORDER_STATUS_CONFIRMED,
        )
        shipment_order_in_transit = cls.create_order_with_related_data(
            customer=cls.customer,
            product=cls.product_out_of_stock,
            status=Order.ORDER_STATUS_CONFIRMED,
        )

        cls.create_shipment_with_related_data(
            order=shipment_order_failed,
            customer=cls.customer,
            status=Shipment.STATUS_FAILED,
        )
        cls.create_shipment_with_related_data(
            order=shipment_order_in_transit,
            customer=cls.customer,
            status=Shipment.STATUS_IN_TRANSIT,
        )

        cls.create_review_with_related_data(
            customer=cls.customer,
            product=cls.product_low_stock,
            status=Review.REVIEW_STATUS_PENDING,
        )
        cls.create_review_with_related_data(
            customer=cls.create_user(),
            product=cls.product_out_of_stock,
            status=Review.REVIEW_STATUS_REJECTED,
        )
        cls.create_review_with_related_data(
            customer=cls.create_user(),
            product=cls.product_without_images,
            status=Review.REVIEW_STATUS_HIDDEN,
        )

        cls.create_notification_with_related_data(
            recipient=cls.customer,
            created_by=cls.staff_user,
            status=Notification.STATUS_FAILED,
        )
        cls.create_notification_with_related_data(
            recipient=cls.customer,
            created_by=cls.staff_user,
            status=Notification.STATUS_PENDING,
        )
        cls.create_notification_with_related_data(
            recipient=cls.customer,
            created_by=cls.staff_user,
            status=Notification.STATUS_UNREAD,
        )

    def test_get_order_operational_metrics_returns_expected_counts(self):
        """Ensure order operational metrics identify pending, processing, and cancelled orders correctly."""
        result = get_order_operational_metrics()

        self.assertEqual(result["pending_orders"], 1)
        self.assertEqual(result["processing_orders"], 1)
        self.assertEqual(result["cancelled_orders"], 1)

    def test_get_payment_operational_metrics_returns_expected_counts(self):
        """Ensure payment operational metrics identify failed, processing, and refunded payments correctly."""
        result = get_payment_operational_metrics()

        self.assertEqual(result["failed_payments"], 1)
        self.assertEqual(result["processing_payments"], 1)
        self.assertEqual(result["refunded_payments"], 1)

    def test_get_shipping_operational_metrics_returns_expected_counts(self):
        """Ensure shipping operational metrics identify delayed, failed, and in-transit shipments correctly."""
        result = get_shipping_operational_metrics()

        self.assertEqual(result["delayed_shipments"], 1)
        self.assertEqual(result["failed_shipments"], 1)
        self.assertEqual(result["in_transit_shipments"], 1)

    def test_get_review_operational_metrics_returns_expected_counts(self):
        """Ensure review operational metrics identify moderation-pending, flagged, and hidden reviews correctly."""
        result = get_review_operational_metrics()

        self.assertEqual(result["pending_moderation"], 1)
        self.assertEqual(result["flagged_reviews"], 1)
        self.assertEqual(result["hidden_reviews"], 1)

    def test_get_notification_operational_metrics_returns_expected_counts(self):
        """Ensure notification operational metrics identify failed, pending, and unread notifications correctly."""
        result = get_notification_operational_metrics()

        self.assertEqual(result["failed_notifications"], 1)
        self.assertEqual(result["pending_notifications"], 1)
        self.assertEqual(result["unread_notifications"], 1)

    def test_get_product_operational_metrics_returns_expected_counts(self):
        """Ensure product operational metrics identify low stock, out of stock, and imageless products correctly."""
        result = get_product_operational_metrics()

        self.assertEqual(result["low_stock_products"], 1)
        self.assertEqual(result["out_of_stock_products"], 1)
        self.assertEqual(result["products_without_images"], 3)


class AdminDashboardRecentActivitySelectorTestCase(
    BaseAdminDashboardSelectorFactoryMixin,
    TestCase,
):
    @classmethod
    def setUpTestData(cls):
        cls.customer = cls.create_user()
        cls.staff_user = cls.create_staff_user()
        cls.product = cls.create_product_with_related_data()

        cls.order = cls.create_order_with_related_data(
            customer=cls.customer,
            product=cls.product,
            status=Order.ORDER_STATUS_PENDING,
        )
        cls.payment_order = cls.create_order_with_related_data(
            customer=cls.customer,
            product=cls.product,
            status=Order.ORDER_STATUS_CONFIRMED,
        )
        cls.payment = cls.create_payment_with_related_data(
            order=cls.payment_order,
            customer=cls.customer,
            status=Payment.PAYMENT_STATUS_CAPTURED,
        )
        cls.shipment_order = cls.create_order_with_related_data(
            customer=cls.customer,
            product=cls.product,
            status=Order.ORDER_STATUS_CONFIRMED,
        )
        cls.shipment = cls.create_shipment_with_related_data(
            order=cls.shipment_order,
            customer=cls.customer,
            status=Shipment.STATUS_IN_TRANSIT,
        )
        cls.review = cls.create_review_with_related_data(
            customer=cls.customer,
            product=cls.product,
            status=Review.REVIEW_STATUS_APPROVED,
        )
        cls.notification = cls.create_notification_with_related_data(
            recipient=cls.customer,
            created_by=cls.staff_user,
            status=Notification.STATUS_UNREAD,
        )
        cls.admin_log = cls.create_admin_log(
            performed_by=cls.staff_user,
            action_type="bulk_review_moderation",
            target_module="reviews",
        )
        cls.product_recent = cls.create_product_with_related_data(
            name="Recent product",
            is_active=True,
        )

    def test_get_recent_order_activity_returns_expected_payload(self):
        """Ensure recent order activity returns the expected payload structure and source metadata."""
        result = get_recent_order_activity(limit=10)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["source"], "orders")
        self.assertEqual(result[0]["type"], "order")
        self.assertIsNotNone(result[0]["entity_id"])
        self.assertIsNotNone(result[0]["status"])
        self.assertIsNotNone(result[0]["created_at"])

    def test_get_recent_payment_activity_returns_expected_payload(self):
        """Ensure recent payment activity returns the expected payload for the captured payment."""
        result = get_recent_payment_activity(limit=10)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["source"], "payments")
        self.assertEqual(result[0]["type"], "payment")
        self.assertEqual(result[0]["entity_id"], str(self.payment.id))
        self.assertEqual(result[0]["status"], self.payment.status)

    def test_get_recent_shipping_activity_returns_expected_payload(self):
        """Ensure recent shipping activity returns the expected payload for the created shipment."""
        result = get_recent_shipping_activity(limit=10)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["source"], "shipping")
        self.assertEqual(result[0]["type"], "shipment")
        self.assertEqual(result[0]["entity_id"], str(self.shipment.id))
        self.assertEqual(result[0]["status"], self.shipment.status)

    def test_get_recent_review_activity_returns_expected_payload(self):
        """Ensure recent review activity returns the expected payload for the created review."""
        result = get_recent_review_activity(limit=10)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["source"], "reviews")
        self.assertEqual(result[0]["type"], "review")
        self.assertEqual(result[0]["entity_id"], str(self.review.id))
        self.assertEqual(result[0]["status"], self.review.status)

    def test_get_recent_notification_activity_returns_expected_payload(self):
        """Ensure recent notification activity returns the expected payload for the created notification."""
        result = get_recent_notification_activity(limit=10)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["source"], "notifications")
        self.assertEqual(result[0]["type"], "notification")
        self.assertEqual(result[0]["entity_id"], str(self.notification.id))
        self.assertEqual(result[0]["status"], self.notification.status)

    def test_get_recent_admin_activity_returns_expected_payload(self):
        """Ensure recent admin activity returns the expected payload for the created dashboard log."""
        result = get_recent_admin_activity(limit=10)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["source"], "admin_dashboard")
        self.assertEqual(result[0]["type"], "admin_action")
        self.assertEqual(result[0]["entity_id"], str(self.admin_log.id))
        self.assertEqual(result[0]["action_type"], self.admin_log.action_type)
        self.assertEqual(result[0]["target_module"], self.admin_log.target_module)

    def test_get_recent_product_activity_returns_expected_payload(self):
        """Ensure recent product activity returns the expected payload for the most recently created active product."""
        result = get_recent_product_activity(limit=10)

        self.assertGreaterEqual(len(result), 1)
        self.assertEqual(result[0]["source"], "products")
        self.assertEqual(result[0]["type"], "product")
        self.assertEqual(result[0]["entity_id"], str(self.product_recent.id))
        self.assertEqual(result[0]["status"], "active")

    def test_recent_activity_selectors_respect_limit(self):
        """Ensure recent activity selectors honor the provided limit when returning order activity."""
        self.create_order_with_related_data(
            customer=self.customer,
            product=self.product,
            status=Order.ORDER_STATUS_SHIPPED,
        )
        self.create_order_with_related_data(
            customer=self.customer,
            product=self.product,
            status=Order.ORDER_STATUS_DELIVERED,
        )

        result = get_recent_order_activity(limit=2)

        self.assertEqual(len(result), 2)