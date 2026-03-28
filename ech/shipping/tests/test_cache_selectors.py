import uuid
from datetime import timedelta

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from ech.users.models import CustomUser
from ech.orders.models import Order
from ech.shipping.models import (
    Shipment,
    ShipmentAddress,
    ShipmentLifecycle,
)
from ech.shipping.selectors import (
    get_shipment_by_id,
    get_shipment_by_order_id,
    list_customer_shipments,
    list_customer_shipments_by_status,
    list_management_shipments,
    search_shipments,
)


class ShippingCacheSelectorsTestCase(TestCase):
    def setUp(self):
        cache.clear()

        self.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.order = Order.objects.create(
            customer=self.customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
            currency="USD",
        )

        self.shipment = Shipment.objects.create(
            order=self.order,
            customer=self.customer,
            status="pending",
            shipping_method="standard",
            carrier_name="DHL",
            tracking_code="TRACK-CACHE",
            external_reference="EXT-CACHE",
            shipping_cost="10.00",
            currency="USD",
            estimated_delivery_date=timezone.localdate() + timedelta(days=5),
            idempotency_key=uuid.uuid4(),
        )

        ShipmentAddress.objects.create(
            shipment=self.shipment,
            full_name="John Doe",
            address_line="123 Main Street",
            city="Sao Paulo",
            state="SP",
            country="Brazil",
            postal_code="01000-000",
        )

        ShipmentLifecycle.objects.create(shipment=self.shipment)

    def test_get_shipment_by_id_uses_cached_detail_snapshot(self):
        """Return cached shipment detail until cache is invalidated."""
        shipment = get_shipment_by_id(shipment_id=self.shipment.id)
        self.assertEqual(shipment.status, "pending")

        Shipment.objects.filter(id=self.shipment.id).update(status="shipped")

        cached_shipment = get_shipment_by_id(shipment_id=self.shipment.id)
        self.assertEqual(cached_shipment.status, "pending")

    def test_get_shipment_by_order_id_uses_cached_lookup(self):
        """Return cached shipment by order lookup until cache is invalidated."""
        shipment = get_shipment_by_order_id(order_id=self.order.id)
        self.assertEqual(shipment.id, self.shipment.id)

        Shipment.objects.filter(id=self.shipment.id).update(status="shipped")

        cached_shipment = get_shipment_by_order_id(order_id=self.order.id)
        self.assertEqual(cached_shipment.status, "pending")

    def test_list_customer_shipments_uses_cached_id_set(self):
        """Return cached customer shipment IDs until cache is invalidated."""
        first_result = list(list_customer_shipments(customer=self.customer))
        self.assertEqual(len(first_result), 1)

        second_order = Order.objects.create(
            customer=self.customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
            currency="USD",
        )

        new_shipment = Shipment.objects.create(
            order=second_order,
            customer=self.customer,
            status="pending",
            shipping_method="standard",
            carrier_name="FedEx",
            tracking_code="TRACK-NEW",
            external_reference="EXT-NEW",
            shipping_cost="10.00",
            currency="USD",
            estimated_delivery_date=timezone.localdate() + timedelta(days=3),
            idempotency_key=uuid.uuid4(),
        )

        ShipmentAddress.objects.create(
            shipment=new_shipment,
            full_name="Jane Doe",
            address_line="456 Other Street",
            city="Rio",
            state="RJ",
            country="Brazil",
            postal_code="20000-000",
        )

        ShipmentLifecycle.objects.create(shipment=new_shipment)

        second_result = list(list_customer_shipments(customer=self.customer))
        self.assertEqual(len(second_result), 1)

    def test_list_customer_shipments_by_status_uses_cached_id_set(self):
        """Return cached filtered customer shipment IDs for repeated identical queries."""
        first_result = list(
            list_customer_shipments_by_status(
                customer=self.customer,
                status="pending",
            )
        )
        second_result = list(
            list_customer_shipments_by_status(
                customer=self.customer,
                status="pending",
            )
        )

        self.assertEqual(len(first_result), 1)
        self.assertEqual(len(second_result), 1)
        self.assertEqual(first_result[0].id, second_result[0].id)

    def test_list_management_shipments_uses_cached_id_set(self):
        """Return cached management shipment IDs until cache is invalidated."""
        first_result = list(list_management_shipments())
        self.assertEqual(len(first_result), 1)

        second_order = Order.objects.create(
            customer=self.customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
            currency="USD",
        )

        new_shipment = Shipment.objects.create(
            order=second_order,
            customer=self.customer,
            status="pending",
            shipping_method="standard",
            carrier_name="UPS",
            tracking_code="TRACK-MGMT",
            external_reference="EXT-MGMT",
            shipping_cost="10.00",
            currency="USD",
            estimated_delivery_date=timezone.localdate() + timedelta(days=4),
            idempotency_key=uuid.uuid4(),
        )

        ShipmentAddress.objects.create(
            shipment=new_shipment,
            full_name="Jane Doe",
            address_line="789 Another Street",
            city="Campinas",
            state="SP",
            country="Brazil",
            postal_code="13000-000",
        )

        ShipmentLifecycle.objects.create(shipment=new_shipment)

        second_result = list(list_management_shipments())
        self.assertEqual(len(second_result), 1)

    def test_search_shipments_uses_cached_result_ids(self):
        """Return cached shipment search IDs for repeated identical queries."""
        first_result = list(search_shipments(query="TRACK-CACHE"))
        second_result = list(search_shipments(query="TRACK-CACHE"))

        self.assertEqual(len(first_result), 1)
        self.assertEqual(len(second_result), 1)
        self.assertEqual(first_result[0].id, second_result[0].id)