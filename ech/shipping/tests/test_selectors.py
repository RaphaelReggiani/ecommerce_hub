import uuid
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ech.orders.models import Order
from ech.shipping.exceptions import (
    ShipmentAccessDeniedException,
    ShipmentNotFoundException,
)
from ech.shipping.models import (
    Shipment,
    ShipmentAddress,
    ShipmentLifecycle,
    ShipmentEvent,
    ShipmentTrackingUpdate,
    ShipmentNote,
)
from ech.shipping.selectors import (
    shipment_base_queryset,
    get_shipment_by_id,
    get_shipment_by_order_id,
    get_customer_shipment,
    list_customer_shipments,
    list_customer_shipments_by_status,
    list_management_shipments,
    list_shipments_by_status,
    list_shipments_by_shipping_method,
    list_shipments_by_carrier,
    list_shipments_due_for_delivery,
    list_shipments_with_tracking_code,
    search_shipments,
)


User = get_user_model()


class BaseShipmentSelectorFactoryMixin:
    def create_user(self, **kwargs):
        suffix = uuid.uuid4().hex[:8]

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

    def create_order(self, **kwargs):
        customer = kwargs.pop("customer", None) or self.create_user()

        data = {
            "customer": customer,
            "status": Order.ORDER_STATUS_PENDING,
            "payment_status": Order.PAYMENT_STATUS_PENDING,
            "shipping_status": Order.SHIPPING_STATUS_PENDING,
            "currency": "USD",
        }
        data.update(kwargs)
        return Order.objects.create(**data)

    def create_shipment(self, **kwargs):
        order = kwargs.pop("order", None) or self.create_order()
        customer = kwargs.pop("customer", None) or order.customer

        data = {
            "order": order,
            "customer": customer,
            "status": Shipment.STATUS_PENDING,
            "shipping_method": Shipment.METHOD_STANDARD,
            "carrier_name": "DHL",
            "tracking_code": f"TRACK-{uuid.uuid4().hex[:10].upper()}",
            "external_reference": f"EXT-{uuid.uuid4().hex[:6].upper()}",
            "shipping_cost": Decimal("19.90"),
            "currency": "USD",
            "estimated_delivery_date": timezone.now().date() + timedelta(days=5),
            "delivered_to_name": "",
            "is_return_to_sender": False,
        }
        data.update(kwargs)
        return Shipment.objects.create(**data)

    def create_shipment_with_related_data(self, **kwargs):
        shipment = self.create_shipment(**kwargs)

        ShipmentAddress.objects.create(
            shipment=shipment,
            full_name="User Tester",
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
            description="Shipment created.",
            event_at=timezone.now(),
        )

        ShipmentNote.objects.create(
            shipment=shipment,
            message="Internal operational note.",
            is_internal=True,
        )

        return shipment


class ShipmentBaseQuerysetTestCase(BaseShipmentSelectorFactoryMixin, TestCase):
    def test_shipment_base_queryset_applies_select_and_prefetch_related(self):
        """Apply select_related and prefetch_related to shipment base queryset."""
        queryset = shipment_base_queryset()

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


class ShipmentRetrievalSelectorTestCase(BaseShipmentSelectorFactoryMixin, TestCase):
    def test_get_shipment_by_id_returns_matching_shipment(self):
        """Return a shipment by identifier using the optimized queryset."""
        shipment = self.create_shipment_with_related_data()

        result = get_shipment_by_id(shipment_id=shipment.id)

        self.assertEqual(result, shipment)
        self.assertEqual(result.address.full_name, "User Tester")
        self.assertIsNotNone(result.lifecycle)
        self.assertEqual(result.events.count(), 1)
        self.assertEqual(result.tracking_updates.count(), 1)
        self.assertEqual(result.notes.count(), 1)

    def test_get_shipment_by_id_raises_not_found_for_unknown_shipment(self):
        """Raise ShipmentNotFoundException for an unknown shipment id."""
        with self.assertRaises(ShipmentNotFoundException):
            get_shipment_by_id(shipment_id=uuid.uuid4())

    def test_get_shipment_by_order_id_returns_matching_shipment(self):
        """Return a shipment by related order identifier."""
        shipment = self.create_shipment_with_related_data()

        result = get_shipment_by_order_id(order_id=shipment.order.id)

        self.assertEqual(result, shipment)

    def test_get_shipment_by_order_id_raises_not_found_for_unknown_order(self):
        """Raise ShipmentNotFoundException for an unknown order id."""
        with self.assertRaises(ShipmentNotFoundException):
            get_shipment_by_order_id(order_id=uuid.uuid4())

    def test_get_customer_shipment_returns_customer_owned_shipment(self):
        """Return a shipment when it belongs to the given customer."""
        customer = self.create_user()
        shipment = self.create_shipment(customer=customer, order=self.create_order(customer=customer))

        result = get_customer_shipment(
            shipment_id=shipment.id,
            customer=customer,
        )

        self.assertEqual(result, shipment)

    def test_get_customer_shipment_raises_not_found_for_unknown_shipment(self):
        """Raise ShipmentNotFoundException when shipment does not exist."""
        customer = self.create_user()

        with self.assertRaises(ShipmentNotFoundException):
            get_customer_shipment(
                shipment_id=uuid.uuid4(),
                customer=customer,
            )

    def test_get_customer_shipment_raises_access_denied_for_other_customer(self):
        """Raise ShipmentAccessDeniedException when shipment belongs to another customer."""
        owner = self.create_user()
        another_customer = self.create_user()
        shipment = self.create_shipment(
            customer=owner,
            order=self.create_order(customer=owner),
        )

        with self.assertRaises(ShipmentAccessDeniedException):
            get_customer_shipment(
                shipment_id=shipment.id,
                customer=another_customer,
            )


class ShipmentListSelectorTestCase(BaseShipmentSelectorFactoryMixin, TestCase):
    def setUp(self):
        self.customer_1 = self.create_user()
        self.customer_2 = self.create_user()

        self.order_1 = self.create_order(customer=self.customer_1)
        self.order_2 = self.create_order(customer=self.customer_1)
        self.order_3 = self.create_order(customer=self.customer_2)

        self.shipment_1 = self.create_shipment(
            order=self.order_1,
            customer=self.customer_1,
            status=Shipment.STATUS_PENDING,
            shipping_method=Shipment.METHOD_STANDARD,
            carrier_name="DHL",
            tracking_code="TRACK-CUST-001",
            external_reference="REF-CUST-001",
            estimated_delivery_date=timezone.now().date() + timedelta(days=2),
        )
        self.shipment_2 = self.create_shipment(
            order=self.order_2,
            customer=self.customer_1,
            status=Shipment.STATUS_SHIPPED,
            shipping_method=Shipment.METHOD_EXPRESS,
            carrier_name="FedEx",
            tracking_code="TRACK-CUST-002",
            external_reference="REF-CUST-002",
            estimated_delivery_date=timezone.now().date() + timedelta(days=4),
        )
        self.shipment_3 = self.create_shipment(
            order=self.order_3,
            customer=self.customer_2,
            status=Shipment.STATUS_IN_TRANSIT,
            shipping_method=Shipment.METHOD_SAME_DAY,
            carrier_name="UPS",
            tracking_code="TRACK-CUST-003",
            external_reference="REF-CUST-003",
            estimated_delivery_date=timezone.now().date() + timedelta(days=4),
        )

    def test_list_customer_shipments_returns_only_customer_shipments(self):
        """List only shipments belonging to the given customer."""
        result = list_customer_shipments(customer=self.customer_1)

        self.assertEqual(result.count(), 2)
        self.assertEqual(list(result), [self.shipment_2, self.shipment_1])

    def test_list_customer_shipments_by_status_filters_customer_shipments(self):
        """List customer shipments filtered by a specific status."""
        result = list_customer_shipments_by_status(
            customer=self.customer_1,
            status_value=Shipment.STATUS_SHIPPED,
        )

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.shipment_2)

    def test_list_management_shipments_returns_all_shipments(self):
        """List all shipments for management in descending creation order."""
        result = list_management_shipments()

        self.assertEqual(result.count(), 3)
        self.assertEqual(list(result), [self.shipment_3, self.shipment_2, self.shipment_1])

    def test_list_shipments_by_status_filters_management_queryset(self):
        """List shipments filtered by status for management use."""
        result = list_shipments_by_status(status_value=Shipment.STATUS_PENDING)

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.shipment_1)

    def test_list_shipments_by_shipping_method_filters_queryset(self):
        """List shipments filtered by shipping method."""
        result = list_shipments_by_shipping_method(
            shipping_method=Shipment.METHOD_EXPRESS,
        )

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.shipment_2)

    def test_list_shipments_by_carrier_filters_case_insensitively(self):
        """List shipments filtered by carrier name using case-insensitive exact match."""
        result = list_shipments_by_carrier(carrier_name="fedex")

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.shipment_2)

    def test_list_shipments_due_for_delivery_filters_by_estimated_date(self):
        """List shipments due for a specific delivery date."""
        target_date = self.shipment_2.estimated_delivery_date

        result = list_shipments_due_for_delivery(delivery_date=target_date)

        self.assertEqual(result.count(), 2)
        self.assertEqual(list(result), [self.shipment_3, self.shipment_2])

    def test_list_shipments_with_tracking_code_excludes_null_and_blank_values(self):
        """List only shipments that already contain a non-empty tracking code."""
        shipment_without_tracking = self.create_shipment(
            order=self.create_order(customer=self.customer_1),
            customer=self.customer_1,
            tracking_code=None,
        )
        shipment_with_blank_tracking = self.create_shipment(
            order=self.create_order(customer=self.customer_1),
            customer=self.customer_1,
            tracking_code="",
        )

        result = list_shipments_with_tracking_code()

        self.assertIn(self.shipment_1, result)
        self.assertIn(self.shipment_2, result)
        self.assertIn(self.shipment_3, result)
        self.assertNotIn(shipment_without_tracking, result)
        self.assertNotIn(shipment_with_blank_tracking, result)

    def test_search_shipments_matches_tracking_code(self):
        """Search shipments by partial tracking code."""
        result = search_shipments(query="CUST-001")

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.shipment_1)

    def test_search_shipments_matches_carrier_name(self):
        """Search shipments by partial carrier name."""
        result = search_shipments(query="fed")

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.shipment_2)

    def test_search_shipments_matches_external_reference(self):
        """Search shipments by partial external reference."""
        result = search_shipments(query="REF-CUST-003")

        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first(), self.shipment_3)

    def test_search_shipments_returns_ordered_results(self):
        """Return matching search results ordered by newest created_at first."""
        self.shipment_2.tracking_code = "SEARCH-SHARED-001"
        self.shipment_2.save(update_fields=["tracking_code"])

        self.shipment_3.tracking_code = "SEARCH-SHARED-002"
        self.shipment_3.save(update_fields=["tracking_code"])

        result = search_shipments(query="SEARCH-SHARED")

        self.assertEqual(list(result), [self.shipment_3, self.shipment_2])