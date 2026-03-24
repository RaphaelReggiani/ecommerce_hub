import uuid
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ech.orders.models import Order
from ech.shipping.filters import ShipmentFilter, ShipmentManagementFilter
from ech.shipping.models import Shipment


User = get_user_model()


class BaseShipmentFilterFactoryMixin:
    def create_user(self):
        suffix = uuid.uuid4().hex[:8]

        return User.objects.create_user(
            email=f"user_{suffix}@test.com",
            password="StrongPassword123",
            user_name=f"User {suffix}",
            role=User.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

    def create_order(self, customer=None):
        customer = customer or self.create_user()

        return Order.objects.create(
            customer=customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
            currency="USD",
        )

    def create_shipment(self, **kwargs):
        order = kwargs.pop("order", None) or self.create_order()
        customer = kwargs.pop("customer", None) or order.customer

        data = {
            "order": order,
            "customer": customer,
            "status": Shipment.STATUS_PENDING,
            "shipping_method": Shipment.METHOD_STANDARD,
            "carrier_name": "DHL",
            "tracking_code": f"TRACK-{uuid.uuid4().hex[:10]}",
            "external_reference": "EXT-REF",
            "shipping_cost": Decimal("10.00"),
            "currency": "USD",
            "estimated_delivery_date": timezone.now().date() + timedelta(days=5),
        }

        data.update(kwargs)

        return Shipment.objects.create(**data)


class ShipmentFilterTestCase(BaseShipmentFilterFactoryMixin, TestCase):
    def setUp(self):
        self.customer = self.create_user()

        self.shipment_1 = self.create_shipment(
            customer=self.customer,
            status=Shipment.STATUS_PENDING,
            shipping_method=Shipment.METHOD_STANDARD,
            carrier_name="DHL",
        )

        self.shipment_2 = self.create_shipment(
            customer=self.customer,
            status=Shipment.STATUS_SHIPPED,
            shipping_method=Shipment.METHOD_EXPRESS,
            carrier_name="FedEx",
        )

    def test_filter_by_status(self):
        """Filter shipments by exact status."""
        queryset = Shipment.objects.all()

        filtered = ShipmentFilter(
            {"status": Shipment.STATUS_PENDING},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.shipment_1)

    def test_filter_by_shipping_method(self):
        """Filter shipments by exact shipping method."""
        queryset = Shipment.objects.all()

        filtered = ShipmentFilter(
            {"shipping_method": Shipment.METHOD_EXPRESS},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.shipment_2)

    def test_filter_by_carrier_name_icontains(self):
        """Filter shipments using partial carrier name match."""
        queryset = Shipment.objects.all()

        filtered = ShipmentFilter(
            {"carrier_name": "dh"},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.shipment_1)

    def test_filter_by_tracking_code_icontains(self):
        """Filter shipments using partial tracking code."""
        queryset = Shipment.objects.all()
        partial = self.shipment_1.tracking_code[:6]

        filtered = ShipmentFilter(
            {"tracking_code": partial},
            queryset=queryset,
        ).qs

        self.assertIn(self.shipment_1, filtered)

    def test_filter_created_after(self):
        """Filter shipments created after a given datetime."""
        queryset = Shipment.objects.all()
        past = timezone.now() - timedelta(days=1)

        filtered = ShipmentFilter(
            {"created_after": past},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 2)

    def test_filter_estimated_delivery_after(self):
        """Filter shipments by estimated delivery date after a given date."""
        queryset = Shipment.objects.all()
        future_date = timezone.now().date() + timedelta(days=3)

        filtered = ShipmentFilter(
            {"estimated_delivery_after": future_date},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 2)


class ShipmentManagementFilterTestCase(BaseShipmentFilterFactoryMixin, TestCase):
    def setUp(self):
        self.customer_1 = self.create_user()
        self.customer_2 = self.create_user()

        self.order_1 = self.create_order(self.customer_1)
        self.order_2 = self.create_order(self.customer_2)

        self.shipment_1 = self.create_shipment(
            order=self.order_1,
            customer=self.customer_1,
            external_reference="REF-AAA",
        )

        self.shipment_2 = self.create_shipment(
            order=self.order_2,
            customer=self.customer_2,
            external_reference="REF-BBB",
        )

    def test_filter_by_external_reference(self):
        """Filter shipments using partial external reference."""
        queryset = Shipment.objects.all()

        filtered = ShipmentManagementFilter(
            {"external_reference": "AAA"},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.shipment_1)

    def test_filter_by_customer_id(self):
        """Filter shipments by customer UUID."""
        queryset = Shipment.objects.all()

        filtered = ShipmentManagementFilter(
            {"customer_id": str(self.customer_1.id)},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.shipment_1)

    def test_filter_by_order_id(self):
        """Filter shipments by order UUID."""
        queryset = Shipment.objects.all()

        filtered = ShipmentManagementFilter(
            {"order_id": str(self.order_2.id)},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.shipment_2)

    def test_filter_by_created_before(self):
        """Filter shipments created before a given datetime."""
        queryset = Shipment.objects.all()
        future = timezone.now() + timedelta(days=1)

        filtered = ShipmentManagementFilter(
            {"created_before": future},
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 2)

    def test_filter_combined_filters(self):
        """Apply multiple filters simultaneously."""
        queryset = Shipment.objects.all()

        filtered = ShipmentManagementFilter(
            {
                "customer_id": str(self.customer_1.id),
                "external_reference": "AAA",
            },
            queryset=queryset,
        ).qs

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first(), self.shipment_1)