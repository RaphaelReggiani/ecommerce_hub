import uuid
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ech.analytics.domain_events.events import (
    AnalyticsSnapshotCreatedEvent,
    AnalyticsSnapshotFailedEvent,
)
from ech.analytics.exceptions import (
    AnalyticsSnapshotAlreadyExistsException,
    AnalyticsSnapshotCreationException,
    IdempotencyConflictException,
)
from ech.analytics.models import (
    AnalyticsEvent,
    AnalyticsSnapshot,
)
from ech.analytics.services.analytic_snapshot_generation_service import (
    AnalyticsSnapshotGenerationService,
)
from ech.orders.models import Order, OrderItem
from ech.payments.models import Payment
from ech.products.models import Product
from ech.reviews.models import Review
from ech.shipping.models import Shipment

User = get_user_model()


class BaseAnalyticsSnapshotGenerationFactoryMixin:
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
        user = User.objects.create_user(**data)

        date_joined = kwargs.get("date_joined")
        if date_joined is not None:
            User.objects.filter(id=user.id).update(date_joined=date_joined)
            user.refresh_from_db()

        return user

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
        user = User.objects.create_user(**data)

        date_joined = kwargs.get("date_joined")
        if date_joined is not None:
            User.objects.filter(id=user.id).update(date_joined=date_joined)
            user.refresh_from_db()

        return user

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
    def create_order(cls, **kwargs):
        customer = kwargs.pop("customer", None) or cls.create_user()
        created_at = kwargs.pop("created_at", None)

        data = {
            "customer": customer,
            "status": Order.ORDER_STATUS_PENDING,
            "payment_status": Order.PAYMENT_STATUS_PENDING,
            "shipping_status": Order.SHIPPING_STATUS_PENDING,
            "currency": "USD",
        }
        data.update(kwargs)
        order = Order.objects.create(**data)

        if created_at is not None:
            Order.objects.filter(id=order.id).update(created_at=created_at)
            order.refresh_from_db()

        return order

    @classmethod
    def create_order_item(cls, *, order, product, quantity):
        unit_price = Decimal("100.00")
        total_price = unit_price * quantity

        return OrderItem.objects.create(
            order=order,
            product=product,
            product_name_snapshot=product.name,
            product_type_snapshot=product.product_type,
            brand_snapshot=product.brand,
            quantity=quantity,
            unit_price=unit_price,
            discount_price=unit_price,
            total_price=total_price,
        )

    @classmethod
    def create_payment(cls, **kwargs):
        order = kwargs.pop("order", None) or cls.create_order()
        customer = kwargs.pop("customer", None) or order.customer
        created_at = kwargs.pop("created_at", None)

        data = {
            "order": order,
            "customer": customer,
            "payment_reference": f"PAY-{cls.unique_suffix().upper()}",
            "method": Payment.PAYMENT_METHOD_PIX,
            "status": Payment.PAYMENT_STATUS_CAPTURED,
            "amount": Decimal("100.00"),
            "refunded_amount": Decimal("0.00"),
            "currency": "USD",
            "gateway_name": "stripe",
            "gateway_payment_id": f"GW-{cls.unique_suffix()}",
            "gateway_customer_id": f"CUST-{cls.unique_suffix()}",
            "metadata": {"source": "test"},
        }
        data.update(kwargs)
        payment = Payment.objects.create(**data)

        if created_at is not None:
            Payment.objects.filter(id=payment.id).update(created_at=created_at)
            payment.refresh_from_db()

        return payment

    @classmethod
    def create_shipment(cls, **kwargs):
        order = kwargs.pop("order", None) or cls.create_order()
        customer = kwargs.pop("customer", None) or order.customer
        created_at = kwargs.pop("created_at", None)

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
            "estimated_delivery_date": timezone.localdate() + timedelta(days=5),
        }
        data.update(kwargs)
        shipment = Shipment.objects.create(**data)

        if created_at is not None:
            Shipment.objects.filter(id=shipment.id).update(created_at=created_at)
            shipment.refresh_from_db()

        return shipment

    @classmethod
    def create_review(cls, **kwargs):
        customer = kwargs.pop("customer", None) or cls.create_user()
        product = kwargs.pop("product", None) or cls.create_product()
        created_at = kwargs.pop("created_at", None)

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
        review = Review.objects.create(**data)

        if created_at is not None:
            Review.objects.filter(id=review.id).update(created_at=created_at)
            review.refresh_from_db()

        return review


class AnalyticsSnapshotGenerationServiceTestCase(
    BaseAnalyticsSnapshotGenerationFactoryMixin,
    TestCase,
):
    @classmethod
    def setUpTestData(cls):
        cls.period_start = timezone.now().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        cls.period_end = cls.period_start + timedelta(days=1)

        cls.analytics_staff = cls.create_staff_user(
            email="analytics.service@company.com",
            date_joined=cls.period_start - timedelta(days=30),
        )
        cls.seller = cls.create_staff_user(
            email="seller.service@company.com",
            date_joined=cls.period_start - timedelta(days=20),
        )

        cls.customer_active = cls.create_user(
            email="customer.active@test.com",
            date_joined=cls.period_start - timedelta(days=10),
        )
        cls.customer_new = cls.create_user(
            email="customer.new@test.com",
            date_joined=cls.period_start + timedelta(hours=2),
        )
        cls.customer_inactive = cls.create_user(
            email="customer.inactive@test.com",
            is_active=False,
            email_confirmed=False,
            date_joined=cls.period_start - timedelta(days=5),
        )

        cls.review_customer_1 = cls.create_user(
            email="review.customer1@test.com",
            date_joined=cls.period_start - timedelta(days=8),
        )
        cls.review_customer_2 = cls.create_user(
            email="review.customer2@test.com",
            date_joined=cls.period_start - timedelta(days=7),
        )
        cls.review_customer_3 = cls.create_user(
            email="review.customer3@test.com",
            date_joined=cls.period_start - timedelta(days=6),
        )
        cls.review_customer_4 = cls.create_user(
            email="review.customer4@test.com",
            date_joined=cls.period_start - timedelta(days=4),
        )
        cls.review_customer_5 = cls.create_user(
            email="review.customer5@test.com",
            date_joined=cls.period_start - timedelta(days=3),
        )
        cls.review_customer_6 = cls.create_user(
            email="review.customer6@test.com",
            date_joined=cls.period_start - timedelta(days=2),
        )

        cls.product_1 = cls.create_product(
            sold_by=cls.seller,
            name="iPhone Test",
        )
        cls.product_2 = cls.create_product(
            sold_by=cls.seller,
            name="Headset Test",
            product_type=Product.HEADSET,
        )

    def setUp(self):
        AnalyticsSnapshot.objects.all().delete()
        cache_clear_targets = []
        _ = cache_clear_targets

    def _create_full_period_dataset(self):
        order_1 = self.create_order(
            customer=self.customer_active,
            status=Order.ORDER_STATUS_PENDING,
            created_at=self.period_start + timedelta(hours=1),
        )
        self.create_order_item(
            order=order_1,
            product=self.product_1,
            quantity=2,
        )

        order_2 = self.create_order(
            customer=self.customer_active,
            status=Order.ORDER_STATUS_PROCESSING,
            created_at=self.period_start + timedelta(hours=2),
        )
        self.create_order_item(
            order=order_2,
            product=self.product_1,
            quantity=1,
        )

        order_3 = self.create_order(
            customer=self.customer_new,
            status=Order.ORDER_STATUS_DELIVERED,
            created_at=self.period_start + timedelta(hours=3),
        )
        self.create_order_item(
            order=order_3,
            product=self.product_2,
            quantity=4,
        )

        order_outside = self.create_order(
            customer=self.customer_active,
            status=Order.ORDER_STATUS_CANCELLED,
            created_at=self.period_start - timedelta(days=5),
        )
        self.create_order_item(
            order=order_outside,
            product=self.product_2,
            quantity=10,
        )

        self.create_payment(
            order=order_1,
            customer=self.customer_active,
            status=Payment.PAYMENT_STATUS_CAPTURED,
            amount=Decimal("100.00"),
            refunded_amount=Decimal("0.00"),
            created_at=self.period_start + timedelta(hours=4),
        )
        self.create_payment(
            order=order_2,
            customer=self.customer_active,
            status=Payment.PAYMENT_STATUS_FAILED,
            amount=Decimal("50.00"),
            refunded_amount=Decimal("0.00"),
            created_at=self.period_start + timedelta(hours=5),
        )
        self.create_payment(
            order=order_3,
            customer=self.customer_new,
            status=Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED,
            amount=Decimal("200.00"),
            refunded_amount=Decimal("50.00"),
            created_at=self.period_start + timedelta(hours=6),
        )
        self.create_payment(
            order=order_1,
            customer=self.customer_active,
            status=Payment.PAYMENT_STATUS_REFUNDED,
            amount=Decimal("300.00"),
            refunded_amount=Decimal("300.00"),
            created_at=self.period_start + timedelta(hours=7),
        )
        self.create_payment(
            order=order_outside,
            customer=self.customer_active,
            status=Payment.PAYMENT_STATUS_CAPTURED,
            amount=Decimal("999.00"),
            refunded_amount=Decimal("0.00"),
            created_at=self.period_start - timedelta(days=2),
        )

        self.create_shipment(
            order=order_1,
            customer=self.customer_active,
            status=Shipment.STATUS_IN_TRANSIT,
            created_at=self.period_start + timedelta(hours=8),
        )
        self.create_shipment(
            order=order_2,
            customer=self.customer_active,
            status=Shipment.STATUS_DELIVERED,
            created_at=self.period_start + timedelta(hours=9),
        )
        self.create_shipment(
            order=order_3,
            customer=self.customer_new,
            status=Shipment.STATUS_FAILED,
            created_at=self.period_start + timedelta(hours=10),
        )
        self.create_shipment(
            order=order_outside,
            customer=self.customer_active,
            status=Shipment.STATUS_DELIVERED,
            created_at=self.period_start - timedelta(days=3),
        )

        self.create_review(
            customer=self.review_customer_1,
            product=self.product_1,
            rating=5,
            status=Review.REVIEW_STATUS_APPROVED,
            is_verified_purchase=True,
            created_at=self.period_start + timedelta(hours=11),
        )
        self.create_review(
            customer=self.review_customer_2,
            product=self.product_1,
            rating=1,
            status=Review.REVIEW_STATUS_APPROVED,
            is_verified_purchase=False,
            created_at=self.period_start + timedelta(hours=12),
        )
        self.create_review(
            customer=self.review_customer_3,
            product=self.product_2,
            rating=5,
            status=Review.REVIEW_STATUS_APPROVED,
            is_verified_purchase=True,
            created_at=self.period_start + timedelta(hours=13),
        )
        self.create_review(
            customer=self.review_customer_4,
            product=self.product_2,
            rating=2,
            status=Review.REVIEW_STATUS_REJECTED,
            is_verified_purchase=False,
            created_at=self.period_start + timedelta(hours=14),
        )
        self.create_review(
            customer=self.review_customer_5,
            product=self.product_1,
            rating=4,
            status=Review.REVIEW_STATUS_HIDDEN,
            is_verified_purchase=False,
            created_at=self.period_start + timedelta(hours=15),
        )
        self.create_review(
            customer=self.review_customer_6,
            product=self.product_2,
            rating=1,
            status=Review.REVIEW_STATUS_CANCELLED,
            is_verified_purchase=False,
            created_at=self.period_start + timedelta(hours=16),
        )
        self.create_review(
            customer=self.customer_active,
            product=self.create_product(
                sold_by=self.seller,
                name="Outside Review Product",
                product_type=Product.MOUSE,
            ),
            rating=5,
            status=Review.REVIEW_STATUS_APPROVED,
            created_at=self.period_start - timedelta(days=1),
        )

    def test_generate_snapshot_creates_snapshot_with_expected_metrics(self):
        self._create_full_period_dataset()

        with patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "AnalyticsLogService.log_snapshot_created"
        ) as log_created_mock, patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "AnalyticsLogService.log_snapshot_metrics_updated"
        ) as log_metrics_mock, patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "DomainEventDispatcher.dispatch"
        ) as dispatch_mock, patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "AnalyticsCacheService.invalidate_after_snapshot_mutation"
        ) as invalidate_mock:
            with self.captureOnCommitCallbacks(execute=True) as callbacks:
                snapshot = AnalyticsSnapshotGenerationService.generate_snapshot(
                    period_type=AnalyticsSnapshot.PERIOD_DAILY,
                    period_start=self.period_start,
                    period_end=self.period_end,
                    performed_by=self.analytics_staff,
                    idempotency_key=uuid.uuid4(),
                    metadata={"source": "unit-test"},
                )

        snapshot.refresh_from_db()

        self.assertEqual(snapshot.period_type, AnalyticsSnapshot.PERIOD_DAILY)
        self.assertEqual(snapshot.period_start, self.period_start)
        self.assertEqual(snapshot.period_end, self.period_end)
        self.assertEqual(snapshot.generated_by, self.analytics_staff)
        self.assertEqual(snapshot.metadata, {"source": "unit-test"})

        self.assertEqual(snapshot.total_orders, 3)
        self.assertEqual(snapshot.orders_pending, 1)
        self.assertEqual(snapshot.orders_processing, 1)
        self.assertEqual(snapshot.orders_shipped, 0)
        self.assertEqual(snapshot.orders_delivered, 1)
        self.assertEqual(snapshot.orders_cancelled, 0)

        self.assertEqual(snapshot.total_revenue, Decimal("600.00"))
        self.assertEqual(snapshot.total_refunds, Decimal("350.00"))
        self.assertEqual(snapshot.net_revenue, Decimal("250.00"))

        self.assertEqual(snapshot.payments_captured, 1)
        self.assertEqual(snapshot.payments_failed, 1)
        self.assertEqual(snapshot.payments_refunded, 2)

        self.assertEqual(snapshot.shipments_in_transit, 1)
        self.assertEqual(snapshot.shipments_delivered, 1)
        self.assertEqual(snapshot.shipments_failed, 1)

        self.assertEqual(snapshot.products_sold, 7)
        self.assertEqual(snapshot.top_product_id, self.product_2.id)

        self.assertEqual(snapshot.active_customers, 2)
        self.assertEqual(snapshot.new_customers, 1)

        self.assertEqual(snapshot.total_registered_users, 11)
        self.assertEqual(snapshot.active_users, 10)
        self.assertEqual(snapshot.inactive_users, 1)
        self.assertEqual(snapshot.confirmed_users, 10)
        self.assertEqual(snapshot.unconfirmed_users, 1)
        self.assertEqual(snapshot.staff_users, 2)
        self.assertEqual(snapshot.customer_users, 9)

        self.assertEqual(snapshot.total_reviews, 6)
        self.assertEqual(snapshot.approved_reviews, 3)
        self.assertEqual(snapshot.rejected_reviews, 1)
        self.assertEqual(snapshot.hidden_reviews, 1)
        self.assertEqual(snapshot.cancelled_reviews, 1)
        self.assertEqual(snapshot.verified_purchase_reviews, 2)
        self.assertEqual(snapshot.average_rating, Decimal("3.67"))
        self.assertEqual(snapshot.low_rated_products_count, 0)
        self.assertEqual(snapshot.high_rated_products_count, 1)

        self.assertIsNotNone(snapshot.lifecycle.generation_started_at)
        self.assertIsNotNone(snapshot.lifecycle.generation_completed_at)

        event_types = list(
            snapshot.events.order_by("created_at").values_list("event_type", flat=True)
        )
        self.assertEqual(
            event_types,
            [
                AnalyticsEvent.TYPE_SNAPSHOT_GENERATION_STARTED,
                AnalyticsEvent.TYPE_SNAPSHOT_CREATED,
                AnalyticsEvent.TYPE_SNAPSHOT_GENERATION_COMPLETED,
            ],
        )

        self.assertEqual(len(callbacks), 1)
        invalidate_mock.assert_called_once_with(
            snapshot_id=snapshot.id,
            period_type=snapshot.period_type,
        )
        log_created_mock.assert_called_once_with(
            snapshot=snapshot,
            performed_by=self.analytics_staff,
        )
        log_metrics_mock.assert_called_once()
        self.assertEqual(dispatch_mock.call_count, 1)

        dispatched_event = dispatch_mock.call_args.args[0]
        self.assertIsInstance(dispatched_event, AnalyticsSnapshotCreatedEvent)
        self.assertEqual(dispatched_event.snapshot_id, snapshot.id)
        self.assertEqual(dispatched_event.generated_by_id, self.analytics_staff.id)

    def test_generate_snapshot_creates_zeroed_snapshot_when_operational_data_is_empty(self):
        with patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "list_orders_for_analytics",
            return_value=[],
        ), patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "list_payments_for_analytics",
            return_value=[],
        ), patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "list_shipments_for_analytics",
            return_value=[],
        ), patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "list_reviews_for_analytics",
            return_value=[],
        ), patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "list_customers_for_analytics",
            return_value=[],
        ), patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "list_users_for_analytics",
            return_value=[],
        ), patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "DomainEventDispatcher.dispatch"
        ), patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "AnalyticsCacheService.invalidate_after_snapshot_mutation"
        ):
            with self.captureOnCommitCallbacks(execute=True):
                snapshot = AnalyticsSnapshotGenerationService.generate_snapshot(
                    period_type=AnalyticsSnapshot.PERIOD_DAILY,
                    period_start=self.period_start,
                    period_end=self.period_end,
                    performed_by=None,
                    idempotency_key=uuid.uuid4(),
                    metadata={"source": "empty-period"},
                )

        snapshot.refresh_from_db()

        self.assertEqual(snapshot.total_orders, 0)
        self.assertEqual(snapshot.total_revenue, Decimal("0.00"))
        self.assertEqual(snapshot.total_refunds, Decimal("0.00"))
        self.assertEqual(snapshot.net_revenue, Decimal("0.00"))
        self.assertEqual(snapshot.payments_captured, 0)
        self.assertEqual(snapshot.payments_failed, 0)
        self.assertEqual(snapshot.payments_refunded, 0)
        self.assertEqual(snapshot.shipments_in_transit, 0)
        self.assertEqual(snapshot.shipments_delivered, 0)
        self.assertEqual(snapshot.shipments_failed, 0)
        self.assertEqual(snapshot.products_sold, 0)
        self.assertIsNone(snapshot.top_product_id)
        self.assertEqual(snapshot.active_customers, 0)
        self.assertEqual(snapshot.new_customers, 0)
        self.assertEqual(snapshot.total_registered_users, 0)
        self.assertEqual(snapshot.active_users, 0)
        self.assertEqual(snapshot.inactive_users, 0)
        self.assertEqual(snapshot.confirmed_users, 0)
        self.assertEqual(snapshot.unconfirmed_users, 0)
        self.assertEqual(snapshot.staff_users, 0)
        self.assertEqual(snapshot.customer_users, 0)
        self.assertEqual(snapshot.total_reviews, 0)
        self.assertEqual(snapshot.approved_reviews, 0)
        self.assertEqual(snapshot.rejected_reviews, 0)
        self.assertEqual(snapshot.hidden_reviews, 0)
        self.assertEqual(snapshot.cancelled_reviews, 0)
        self.assertEqual(snapshot.verified_purchase_reviews, 0)
        self.assertEqual(snapshot.average_rating, Decimal("0.00"))
        self.assertEqual(snapshot.low_rated_products_count, 0)
        self.assertEqual(snapshot.high_rated_products_count, 0)

    def test_generate_snapshot_returns_existing_snapshot_for_same_idempotency_key(self):
        idempotency_key = uuid.uuid4()

        existing_snapshot = self._create_existing_snapshot(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start,
            period_end=self.period_end,
            idempotency_key=idempotency_key,
        )

        with patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "DomainEventDispatcher.dispatch"
        ) as dispatch_mock, patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "AnalyticsCacheService.invalidate_after_snapshot_mutation"
        ) as invalidate_mock:
            snapshot = AnalyticsSnapshotGenerationService.generate_snapshot(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
                performed_by=self.analytics_staff,
                idempotency_key=idempotency_key,
                metadata={"source": "idempotent-replay"},
            )

        self.assertEqual(snapshot.id, existing_snapshot.id)
        self.assertEqual(AnalyticsSnapshot.objects.count(), 1)
        dispatch_mock.assert_not_called()
        invalidate_mock.assert_not_called()

    def test_generate_snapshot_raises_already_exists_without_idempotency_key(self):
        self._create_existing_snapshot(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start,
            period_end=self.period_end,
            idempotency_key=uuid.uuid4(),
        )

        with self.assertRaises(AnalyticsSnapshotAlreadyExistsException):
            AnalyticsSnapshotGenerationService.generate_snapshot(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
                performed_by=self.analytics_staff,
                idempotency_key=None,
            )

    def test_generate_snapshot_raises_already_exists_for_new_key_same_period(self):
        self._create_existing_snapshot(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start,
            period_end=self.period_end,
            idempotency_key=uuid.uuid4(),
        )

        with self.assertRaises(AnalyticsSnapshotAlreadyExistsException):
            AnalyticsSnapshotGenerationService.generate_snapshot(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
                performed_by=self.analytics_staff,
                idempotency_key=uuid.uuid4(),
            )

    def test_generate_snapshot_raises_idempotency_conflict_for_reused_key_other_period(self):
        reused_key = uuid.uuid4()

        self._create_existing_snapshot(
            period_type=AnalyticsSnapshot.PERIOD_WEEKLY,
            period_start=self.period_start - timedelta(days=7),
            period_end=self.period_end - timedelta(days=7),
            idempotency_key=reused_key,
        )
        self._create_existing_snapshot(
            period_type=AnalyticsSnapshot.PERIOD_DAILY,
            period_start=self.period_start,
            period_end=self.period_end,
            idempotency_key=uuid.uuid4(),
        )

        with self.assertRaises(IdempotencyConflictException):
            AnalyticsSnapshotGenerationService.generate_snapshot(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=self.period_end,
                performed_by=self.analytics_staff,
                idempotency_key=reused_key,
            )

    def test_generate_snapshot_normalizes_date_bounds(self):
        period_start_date = self.period_start.date()
        period_end_date = self.period_end.date()

        with patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "DomainEventDispatcher.dispatch"
        ), patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "AnalyticsCacheService.invalidate_after_snapshot_mutation"
        ):
            with self.captureOnCommitCallbacks(execute=True):
                snapshot = AnalyticsSnapshotGenerationService.generate_snapshot(
                    period_type=AnalyticsSnapshot.PERIOD_DAILY,
                    period_start=period_start_date,
                    period_end=period_end_date,
                    performed_by=self.analytics_staff,
                    idempotency_key=uuid.uuid4(),
                )

        expected_start = timezone.make_aware(
            timezone.datetime.combine(period_start_date, timezone.datetime.min.time()),
            timezone.get_current_timezone(),
        )
        expected_end = timezone.make_aware(
            timezone.datetime.combine(period_end_date, timezone.datetime.min.time()),
            timezone.get_current_timezone(),
        )

        self.assertEqual(snapshot.period_start, expected_start)
        self.assertEqual(snapshot.period_end, expected_end)

    def test_generate_snapshot_raises_creation_exception_when_only_one_bound_is_provided(self):
        with self.assertRaises(AnalyticsSnapshotCreationException):
            AnalyticsSnapshotGenerationService.generate_snapshot(
                period_type=AnalyticsSnapshot.PERIOD_DAILY,
                period_start=self.period_start,
                period_end=None,
                performed_by=self.analytics_staff,
                idempotency_key=uuid.uuid4(),
            )

    def test_generate_snapshot_dispatches_failure_event_when_creation_fails(self):
        with patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "AnalyticsSnapshot.objects.create",
            side_effect=Exception("boom"),
        ), patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "DomainEventDispatcher.dispatch"
        ) as dispatch_mock:
            with self.assertRaises(AnalyticsSnapshotCreationException):
                AnalyticsSnapshotGenerationService.generate_snapshot(
                    period_type=AnalyticsSnapshot.PERIOD_DAILY,
                    period_start=self.period_start,
                    period_end=self.period_end,
                    performed_by=self.analytics_staff,
                    idempotency_key=uuid.uuid4(),
                )

        self.assertEqual(dispatch_mock.call_count, 1)
        failed_event = dispatch_mock.call_args.args[0]
        self.assertIsInstance(failed_event, AnalyticsSnapshotFailedEvent)
        self.assertIsNone(failed_event.snapshot_id)
        self.assertEqual(failed_event.period_type, AnalyticsSnapshot.PERIOD_DAILY)
        self.assertEqual(failed_event.period_start, self.period_start)
        self.assertEqual(failed_event.period_end, self.period_end)
        self.assertEqual(failed_event.performed_by_id, self.analytics_staff.id)
        self.assertIn("boom", failed_event.error_message)

    def test_build_snapshot_metrics_returns_empty_payload_when_all_selectors_are_empty(self):
        with patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "list_orders_for_analytics",
            return_value=[],
        ), patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "list_payments_for_analytics",
            return_value=[],
        ), patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "list_shipments_for_analytics",
            return_value=[],
        ), patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "list_reviews_for_analytics",
            return_value=[],
        ), patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "list_customers_for_analytics",
            return_value=[],
        ), patch(
            "ech.analytics.services.analytic_snapshot_generation_service."
            "list_users_for_analytics",
            return_value=[],
        ):
            metrics = AnalyticsSnapshotGenerationService._build_snapshot_metrics(
                period_start=self.period_start,
                period_end=self.period_end,
            )

        self.assertEqual(metrics["total_orders"], 0)
        self.assertEqual(metrics["total_revenue"], Decimal("0.00"))
        self.assertEqual(metrics["net_revenue"], Decimal("0.00"))
        self.assertEqual(metrics["payments_captured"], 0)
        self.assertEqual(metrics["shipments_delivered"], 0)
        self.assertEqual(metrics["products_sold"], 0)
        self.assertEqual(metrics["active_customers"], 0)
        self.assertEqual(metrics["total_registered_users"], 0)
        self.assertEqual(metrics["total_reviews"], 0)
        self.assertEqual(metrics["average_rating"], Decimal("0.00"))
        self.assertIsNone(metrics["top_product_id"])

    def _create_existing_snapshot(
        self,
        *,
        period_type,
        period_start,
        period_end,
        idempotency_key,
    ):
        snapshot = AnalyticsSnapshot.objects.create(
            period_type=period_type,
            period_start=period_start,
            period_end=period_end,
            generated_by=self.analytics_staff,
            idempotency_key=idempotency_key,
            total_orders=1,
            orders_pending=1,
            orders_processing=0,
            orders_shipped=0,
            orders_delivered=0,
            orders_cancelled=0,
            total_revenue=Decimal("10.00"),
            total_refunds=Decimal("0.00"),
            net_revenue=Decimal("10.00"),
            payments_captured=1,
            payments_failed=0,
            payments_refunded=0,
            shipments_in_transit=0,
            shipments_delivered=0,
            shipments_failed=0,
            products_sold=1,
            active_customers=1,
            new_customers=0,
            total_registered_users=1,
            active_users=1,
            inactive_users=0,
            confirmed_users=1,
            unconfirmed_users=0,
            staff_users=1,
            customer_users=0,
            total_reviews=0,
            approved_reviews=0,
            rejected_reviews=0,
            hidden_reviews=0,
            cancelled_reviews=0,
            verified_purchase_reviews=0,
            average_rating=Decimal("0.00"),
            low_rated_products_count=0,
            high_rated_products_count=0,
            metadata={"source": "existing"},
        )
        return snapshot