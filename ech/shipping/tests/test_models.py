from datetime import timedelta
from decimal import Decimal
import uuid

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from ech.orders.models import Order
from ech.shipping.constants.messages import SHIPMENT_NOTE_HELP_TEXT
from ech.shipping.models import (
    Shipment,
    ShipmentAddress,
    ShipmentLifecycle,
    ShipmentEvent,
    ShipmentTrackingUpdate,
    ShipmentNote,
)


User = get_user_model()


class BaseShipmentModelFactoryMixin:
    def create_user(self, **kwargs):
        unique_suffix = uuid.uuid4().hex[:8]

        data = {
            "email": f"customer_{unique_suffix}@test.com",
            "password": "StrongPassword123",
            "user_name": f"Customer User {unique_suffix}",
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
            "external_reference": "EXT-001",
            "shipping_cost": Decimal("19.90"),
            "currency": "USD",
            "estimated_delivery_date": timezone.now().date() + timedelta(days=5),
            "delivered_to_name": "",
            "is_return_to_sender": False,
        }
        data.update(kwargs)
        return Shipment.objects.create(**data)


class ShipmentModelTestCase(BaseShipmentModelFactoryMixin, TestCase):
    def test_shipment_creation_success(self):
        """Create a shipment successfully with operational fields."""
        shipment = self.create_shipment()

        self.assertIsInstance(shipment.id, uuid.UUID)
        self.assertEqual(shipment.status, Shipment.STATUS_PENDING)
        self.assertEqual(shipment.shipping_method, Shipment.METHOD_STANDARD)
        self.assertEqual(shipment.carrier_name, "DHL")
        self.assertEqual(shipment.external_reference, "EXT-001")
        self.assertEqual(shipment.shipping_cost, Decimal("19.90"))
        self.assertEqual(shipment.currency, "USD")
        self.assertFalse(shipment.is_return_to_sender)
        self.assertIsNotNone(shipment.created_at)
        self.assertIsNotNone(shipment.updated_at)

    def test_shipment_defaults_are_applied(self):
        """Apply shipment default values when optional fields are omitted."""
        order = self.create_order()
        shipment = Shipment.objects.create(
            order=order,
            customer=order.customer,
            status=Shipment.STATUS_PENDING,
        )

        self.assertEqual(shipment.shipping_method, Shipment.METHOD_STANDARD)
        self.assertEqual(shipment.carrier_name, "")
        self.assertIsNone(shipment.tracking_code)
        self.assertIsNone(shipment.external_reference)
        self.assertEqual(shipment.shipping_cost, Decimal("0"))
        self.assertEqual(shipment.currency, "USD")
        self.assertIsNone(shipment.estimated_delivery_date)
        self.assertEqual(shipment.delivered_to_name, "")
        self.assertFalse(shipment.is_return_to_sender)
        self.assertIsNone(shipment.idempotency_key)

    def test_shipment_string_representation(self):
        """Return the shipment identifier in string representation."""
        shipment = self.create_shipment()
        self.assertEqual(str(shipment), f"Shipment {shipment.id}")

    def test_shipment_related_names_work_correctly(self):
        """Expose shipment through order and customer related names."""
        shipment = self.create_shipment()

        self.assertEqual(shipment.order.shipment, shipment)
        self.assertIn(shipment, shipment.customer.shipments.all())

    def test_shipment_ordering_by_created_at_desc(self):
        """Order shipments by newest created_at first."""
        first = self.create_shipment(
            order=self.create_order(),
            tracking_code=f"TRACK-{uuid.uuid4().hex[:10].upper()}",
        )
        second = self.create_shipment(
            order=self.create_order(customer=first.customer),
            tracking_code=f"TRACK-{uuid.uuid4().hex[:10].upper()}",
        )

        shipments = list(Shipment.objects.all())

        self.assertEqual(shipments[0], second)
        self.assertEqual(shipments[1], first)

    def test_shipment_tracking_code_must_be_unique(self):
        """Prevent duplicate tracking codes across shipments."""
        tracking_code = "TRACK-UNIQUE-001"
        self.create_shipment(tracking_code=tracking_code)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_shipment(
                    order=self.create_order(),
                    tracking_code=tracking_code,
                )

    def test_shipment_idempotency_key_must_be_unique(self):
        """Prevent duplicate idempotency keys across shipments."""
        idempotency_key = uuid.uuid4()
        self.create_shipment(idempotency_key=idempotency_key)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_shipment(
                    order=self.create_order(),
                    idempotency_key=idempotency_key,
                )

    def test_shipment_meta_ordering_is_configured(self):
        """Configure shipment default ordering by created_at descending."""
        self.assertEqual(Shipment._meta.ordering, ["-created_at"])

    def test_shipment_meta_indexes_are_configured(self):
        """Configure shipment indexes for operational queries."""
        index_names = {index.name for index in Shipment._meta.indexes}

        self.assertIn("ship_cust_created_idx", index_names)
        self.assertIn("ship_status_idx", index_names)
        self.assertIn("ship_track_idx", index_names)
        self.assertIn("ship_est_deliv_idx", index_names)

    def test_shipment_status_choices_include_expected_values(self):
        """Expose all supported shipment lifecycle statuses."""
        choices = dict(Shipment.STATUS_CHOICES)

        self.assertIn(Shipment.STATUS_PENDING, choices)
        self.assertIn(Shipment.STATUS_PREPARING, choices)
        self.assertIn(Shipment.STATUS_READY_TO_SHIP, choices)
        self.assertIn(Shipment.STATUS_SHIPPED, choices)
        self.assertIn(Shipment.STATUS_IN_TRANSIT, choices)
        self.assertIn(Shipment.STATUS_OUT_FOR_DELIVERY, choices)
        self.assertIn(Shipment.STATUS_DELIVERED, choices)
        self.assertIn(Shipment.STATUS_FAILED, choices)
        self.assertIn(Shipment.STATUS_RETURNED, choices)
        self.assertIn(Shipment.STATUS_CANCELLED, choices)

    def test_shipment_method_choices_include_expected_values(self):
        """Expose all supported shipment methods."""
        choices = dict(Shipment.METHOD_CHOICES)

        self.assertIn(Shipment.METHOD_STANDARD, choices)
        self.assertIn(Shipment.METHOD_EXPRESS, choices)
        self.assertIn(Shipment.METHOD_SAME_DAY, choices)
        self.assertIn(Shipment.METHOD_PICKUP_POINT, choices)

    def test_shipment_field_metadata_is_configured(self):
        """Configure optional shipment field metadata correctly."""
        tracking_code_field = Shipment._meta.get_field("tracking_code")
        external_reference_field = Shipment._meta.get_field("external_reference")
        delivered_to_name_field = Shipment._meta.get_field("delivered_to_name")

        self.assertTrue(tracking_code_field.null)
        self.assertTrue(tracking_code_field.blank)
        self.assertTrue(tracking_code_field.unique)

        self.assertTrue(external_reference_field.null)
        self.assertTrue(external_reference_field.blank)
        self.assertEqual(
            external_reference_field.help_text,
            "Reference used by external carrier or shipping gateway.",
        )

        self.assertEqual(
            delivered_to_name_field.help_text,
            "Optional recipient confirmation name for delivery.",
        )


class ShipmentAddressModelTestCase(BaseShipmentModelFactoryMixin, TestCase):
    def test_shipment_address_creation_success(self):
        """Create a shipment address successfully."""
        shipment = self.create_shipment()
        address = ShipmentAddress.objects.create(
            shipment=shipment,
            full_name="User Tester",
            address_line="Av. Paulista, 1000",
            city="Sao Paulo",
            state="SP",
            country="Brazil",
            postal_code="01310-100",
            phone="11999999999",
            delivery_instructions="Leave at concierge.",
        )

        self.assertEqual(address.shipment, shipment)
        self.assertEqual(address.full_name, "User Tester")
        self.assertEqual(address.city, "Sao Paulo")
        self.assertEqual(address.delivery_instructions, "Leave at concierge.")
        self.assertIsNotNone(address.created_at)
        self.assertIsNotNone(address.updated_at)

    def test_shipment_address_string_representation(self):
        """Return recipient and city in shipment address string representation."""
        address = ShipmentAddress.objects.create(
            shipment=self.create_shipment(),
            full_name="John Doe",
            address_line="Street 1",
            city="Los Angeles",
            state="CA",
            country="USA",
            postal_code="90001",
        )

        self.assertEqual(str(address), "John Doe - Los Angeles")

    def test_shipment_address_related_name_works_correctly(self):
        """Expose shipment address through its one-to-one related name."""
        shipment = self.create_shipment()
        address = ShipmentAddress.objects.create(
            shipment=shipment,
            full_name="Jane Doe",
            address_line="Street 2",
            city="Chicago",
            state="IL",
            country="USA",
            postal_code="60601",
        )

        self.assertEqual(shipment.address, address)


class ShipmentLifecycleModelTestCase(BaseShipmentModelFactoryMixin, TestCase):
    def test_shipment_lifecycle_creation_success(self):
        """Create shipment lifecycle timestamps successfully."""
        shipment = self.create_shipment()
        now = timezone.now()

        lifecycle = ShipmentLifecycle.objects.create(
            shipment=shipment,
            preparing_at=now,
            ready_to_ship_at=now,
        )

        self.assertEqual(lifecycle.shipment, shipment)
        self.assertEqual(lifecycle.preparing_at, now)
        self.assertEqual(lifecycle.ready_to_ship_at, now)
        self.assertIsNone(lifecycle.delivered_at)
        self.assertIsNotNone(lifecycle.created_at)
        self.assertIsNotNone(lifecycle.updated_at)

    def test_shipment_lifecycle_string_representation(self):
        """Return shipment identifier in lifecycle string representation."""
        shipment = self.create_shipment()
        lifecycle = ShipmentLifecycle.objects.create(shipment=shipment)

        self.assertEqual(
            str(lifecycle),
            f"Lifecycle for Shipment {shipment.id}",
        )

    def test_shipment_lifecycle_related_name_works_correctly(self):
        """Expose lifecycle through shipment one-to-one related name."""
        shipment = self.create_shipment()
        lifecycle = ShipmentLifecycle.objects.create(shipment=shipment)

        self.assertEqual(shipment.lifecycle, lifecycle)


class ShipmentEventModelTestCase(BaseShipmentModelFactoryMixin, TestCase):
    def test_shipment_event_creation_success(self):
        """Create a shipment audit event successfully."""
        shipment = self.create_shipment()
        operator = self.create_user(
            email="ops@company.com",
            user_name="Operations User",
            role=User.ROLE_OPERATIONS_STAFF,
        )

        event = ShipmentEvent.objects.create(
            shipment=shipment,
            event_type=ShipmentEvent.TYPE_CREATED,
            performed_by=operator,
            metadata={"source": "unit-test"},
        )

        self.assertEqual(event.shipment, shipment)
        self.assertEqual(event.event_type, ShipmentEvent.TYPE_CREATED)
        self.assertEqual(event.performed_by, operator)
        self.assertEqual(event.metadata, {"source": "unit-test"})
        self.assertIsNotNone(event.created_at)

    def test_shipment_event_string_representation(self):
        """Return event type and shipment identifier in string representation."""
        shipment = self.create_shipment()
        event = ShipmentEvent.objects.create(
            shipment=shipment,
            event_type=ShipmentEvent.TYPE_SHIPPED,
        )

        self.assertEqual(
            str(event),
            f"{ShipmentEvent.TYPE_SHIPPED} - {shipment.id}",
        )

    def test_shipment_event_ordering_by_created_at_desc(self):
        """Order shipment events by newest created_at first."""
        shipment = self.create_shipment()
        first = ShipmentEvent.objects.create(
            shipment=shipment,
            event_type=ShipmentEvent.TYPE_CREATED,
        )
        second = ShipmentEvent.objects.create(
            shipment=shipment,
            event_type=ShipmentEvent.TYPE_UPDATED,
        )

        events = list(ShipmentEvent.objects.all())

        self.assertEqual(events[0], second)
        self.assertEqual(events[1], first)

    def test_shipment_event_meta_is_configured(self):
        """Configure shipment event ordering and indexes correctly."""
        self.assertEqual(ShipmentEvent._meta.ordering, ["-created_at"])

        index_names = {index.name for index in ShipmentEvent._meta.indexes}
        self.assertIn("shipevent_ship_created", index_names)

    def test_shipment_event_choices_include_expected_values(self):
        """Expose all supported shipment event types."""
        choices = dict(ShipmentEvent.SHIPMENT_EVENT_TYPE_CHOICES)

        self.assertIn(ShipmentEvent.TYPE_CREATED, choices)
        self.assertIn(ShipmentEvent.TYPE_UPDATED, choices)
        self.assertIn(ShipmentEvent.TYPE_STATUS_CHANGED, choices)
        self.assertIn(ShipmentEvent.TYPE_PREPARING_STARTED, choices)
        self.assertIn(ShipmentEvent.TYPE_READY_TO_SHIP, choices)
        self.assertIn(ShipmentEvent.TYPE_SHIPPED, choices)
        self.assertIn(ShipmentEvent.TYPE_IN_TRANSIT, choices)
        self.assertIn(ShipmentEvent.TYPE_OUT_FOR_DELIVERY, choices)
        self.assertIn(ShipmentEvent.TYPE_DELIVERED, choices)
        self.assertIn(ShipmentEvent.TYPE_FAILED, choices)
        self.assertIn(ShipmentEvent.TYPE_RETURNED, choices)
        self.assertIn(ShipmentEvent.TYPE_CANCELLED, choices)
        self.assertIn(ShipmentEvent.TYPE_TRACKING_UPDATED, choices)


class ShipmentTrackingUpdateModelTestCase(BaseShipmentModelFactoryMixin, TestCase):
    def test_shipment_tracking_update_creation_success(self):
        """Create a tracking update successfully for a shipment."""
        shipment = self.create_shipment()
        event_at = timezone.now()

        update = ShipmentTrackingUpdate.objects.create(
            shipment=shipment,
            status=Shipment.STATUS_IN_TRANSIT,
            location="Sao Paulo Distribution Center",
            description="Package arrived at hub.",
            raw_payload={"carrier_status": "hub_received"},
            event_at=event_at,
        )

        self.assertEqual(update.shipment, shipment)
        self.assertEqual(update.status, Shipment.STATUS_IN_TRANSIT)
        self.assertEqual(update.location, "Sao Paulo Distribution Center")
        self.assertEqual(update.description, "Package arrived at hub.")
        self.assertEqual(update.raw_payload, {"carrier_status": "hub_received"})
        self.assertEqual(update.event_at, event_at)

    def test_shipment_tracking_update_string_representation(self):
        """Return shipment identifier in tracking update string representation."""
        shipment = self.create_shipment()
        update = ShipmentTrackingUpdate.objects.create(
            shipment=shipment,
            description="Tracking created.",
            event_at=timezone.now(),
        )

        self.assertEqual(
            str(update),
            f"Tracking update for {shipment.id}",
        )

    def test_shipment_tracking_update_ordering_by_event_at_desc(self):
        """Order tracking updates by newest event_at first."""
        shipment = self.create_shipment()
        older = ShipmentTrackingUpdate.objects.create(
            shipment=shipment,
            description="Older event",
            event_at=timezone.now() - timedelta(hours=2),
        )
        newer = ShipmentTrackingUpdate.objects.create(
            shipment=shipment,
            description="Newer event",
            event_at=timezone.now(),
        )

        updates = list(ShipmentTrackingUpdate.objects.all())

        self.assertEqual(updates[0], newer)
        self.assertEqual(updates[1], older)

    def test_shipment_tracking_update_meta_is_configured(self):
        """Configure tracking update ordering and indexes correctly."""
        self.assertEqual(
            ShipmentTrackingUpdate._meta.ordering,
            ["-event_at", "-created_at"],
        )

        index_names = {
            index.name for index in ShipmentTrackingUpdate._meta.indexes
        }
        self.assertIn("shiptrack_ship_event_idx", index_names)

    def test_shipment_tracking_update_field_metadata_is_configured(self):
        """Configure tracking update optional field metadata correctly."""
        raw_payload_field = ShipmentTrackingUpdate._meta.get_field("raw_payload")
        status_field = ShipmentTrackingUpdate._meta.get_field("status")
        location_field = ShipmentTrackingUpdate._meta.get_field("location")

        self.assertTrue(raw_payload_field.null)
        self.assertTrue(raw_payload_field.blank)
        self.assertEqual(
            raw_payload_field.help_text,
            "Optional original payload from carrier integration.",
        )
        self.assertTrue(status_field.blank)
        self.assertTrue(location_field.blank)


class ShipmentNoteModelTestCase(BaseShipmentModelFactoryMixin, TestCase):
    def test_shipment_note_creation_success(self):
        """Create a shipment note successfully."""
        shipment = self.create_shipment()
        author = self.create_user(
            email="support@company.com",
            user_name="Support User",
            role=User.ROLE_SUPPORT_STAFF,
        )

        note = ShipmentNote.objects.create(
            shipment=shipment,
            author=author,
            message="Customer requested delivery at front desk.",
            is_internal=True,
        )

        self.assertEqual(note.shipment, shipment)
        self.assertEqual(note.author, author)
        self.assertEqual(
            note.message,
            "Customer requested delivery at front desk.",
        )
        self.assertTrue(note.is_internal)
        self.assertIsNotNone(note.created_at)

    def test_shipment_note_string_representation(self):
        """Return shipment identifier in note string representation."""
        shipment = self.create_shipment()
        note = ShipmentNote.objects.create(
            shipment=shipment,
            author=None,
            message="Operational note.",
        )

        self.assertEqual(str(note), f"Note on {shipment.id}")

    def test_shipment_note_ordering_by_created_at_asc(self):
        """Order shipment notes by oldest created_at first."""
        shipment = self.create_shipment()
        first = ShipmentNote.objects.create(
            shipment=shipment,
            message="First note.",
        )
        second = ShipmentNote.objects.create(
            shipment=shipment,
            message="Second note.",
        )

        notes = list(ShipmentNote.objects.all())

        self.assertEqual(notes[0], first)
        self.assertEqual(notes[1], second)

    def test_shipment_note_meta_is_configured(self):
        """Configure shipment note ordering and indexes correctly."""
        self.assertEqual(ShipmentNote._meta.ordering, ["created_at"])

        index_names = {index.name for index in ShipmentNote._meta.indexes}
        self.assertIn("shipnote_ship_created", index_names)

    def test_shipment_note_help_text_is_configured(self):
        """Configure internal note help text correctly."""
        is_internal_field = ShipmentNote._meta.get_field("is_internal")

        self.assertEqual(is_internal_field.help_text, SHIPMENT_NOTE_HELP_TEXT)
        self.assertFalse(is_internal_field.default)