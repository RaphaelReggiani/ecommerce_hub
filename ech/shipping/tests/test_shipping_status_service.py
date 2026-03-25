from unittest.mock import patch
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ech.orders.models import Order
from ech.shipping.exceptions import (
    InvalidShipmentStatusTransitionException,
    ShipmentAlreadyCancelledException,
    ShipmentAlreadyDeliveredException,
)
from ech.shipping.models import (
    Shipment,
    ShipmentEvent,
    ShipmentLifecycle,
)
from ech.shipping.services.shipping_status_service import ShippingStatusService


User = get_user_model()


class BaseShippingStatusFactoryMixin:
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
            "currency": "USD",
        }
        data.update(kwargs)

        shipment = Shipment.objects.create(**data)
        ShipmentLifecycle.objects.create(shipment=shipment)
        return shipment


class ShippingStatusServiceTestCase(BaseShippingStatusFactoryMixin, TestCase):
    @patch("ech.shipping.services.shipping_status_service.DomainEventDispatcher.dispatch")
    @patch("ech.shipping.services.shipping_status_service.ShippingLogService.log_shipment_status_changed")
    @patch("ech.shipping.services.shipping_status_service.ShipmentStatusChangedEvent")
    def test_update_status_success_creates_events_and_updates_lifecycle(
        self,
        shipment_status_changed_event_mock,
        log_status_changed_mock,
        dispatch_mock,
    ):
        """Update shipment status successfully with events and lifecycle timestamp."""
        shipment = self.create_shipment(status=Shipment.STATUS_PENDING)
        performed_by = self.create_user(
            email="ops@company.com",
            user_name="Operations User",
            role=User.ROLE_OPERATIONS_STAFF,
        )

        updated_shipment = ShippingStatusService.update_status(
            shipment=shipment,
            new_status=Shipment.STATUS_PREPARING,
            performed_by=performed_by,
            metadata={"source": "unit-test"},
        )

        updated_shipment.refresh_from_db()
        updated_shipment.lifecycle.refresh_from_db()

        self.assertEqual(updated_shipment.status, Shipment.STATUS_PREPARING)
        self.assertIsNotNone(updated_shipment.lifecycle.preparing_at)

        events = list(updated_shipment.events.order_by("created_at"))
        self.assertEqual(len(events), 2)

        self.assertEqual(events[0].event_type, ShipmentEvent.TYPE_STATUS_CHANGED)
        self.assertEqual(events[0].performed_by, performed_by)
        self.assertEqual(
            events[0].metadata,
            {
                "previous_status": Shipment.STATUS_PENDING,
                "new_status": Shipment.STATUS_PREPARING,
                "source": "unit-test",
            },
        )

        self.assertEqual(events[1].event_type, ShipmentEvent.TYPE_PREPARING_STARTED)
        self.assertEqual(events[1].performed_by, performed_by)
        self.assertEqual(events[1].metadata, {"source": "unit-test"})

        log_status_changed_mock.assert_called_once_with(
            shipment=updated_shipment,
            previous_status=Shipment.STATUS_PENDING,
            new_status=Shipment.STATUS_PREPARING,
            performed_by=performed_by,
        )

        shipment_status_changed_event_mock.assert_called_once_with(
            shipment_id=updated_shipment.id,
            previous_status=Shipment.STATUS_PENDING,
            new_status=Shipment.STATUS_PREPARING,
            performed_by_id=performed_by.id,
        )
        dispatch_mock.assert_called_once_with(
            shipment_status_changed_event_mock.return_value
        )

    @patch("ech.shipping.services.shipping_status_service.DomainEventDispatcher.dispatch")
    @patch("ech.shipping.services.shipping_status_service.ShippingLogService.log_shipment_status_changed")
    def test_update_status_success_without_metadata(
        self,
        log_status_changed_mock,
        dispatch_mock,
    ):
        """Update shipment status successfully without optional metadata."""
        shipment = self.create_shipment(status=Shipment.STATUS_PREPARING)

        updated_shipment = ShippingStatusService.update_status(
            shipment=shipment,
            new_status=Shipment.STATUS_READY_TO_SHIP,
        )

        updated_shipment.refresh_from_db()
        updated_shipment.lifecycle.refresh_from_db()

        self.assertEqual(updated_shipment.status, Shipment.STATUS_READY_TO_SHIP)
        self.assertIsNotNone(updated_shipment.lifecycle.ready_to_ship_at)

        events = list(updated_shipment.events.order_by("created_at"))
        self.assertEqual(len(events), 2)

        self.assertEqual(
            events[0].metadata,
            {
                "previous_status": Shipment.STATUS_PREPARING,
                "new_status": Shipment.STATUS_READY_TO_SHIP,
            },
        )
        self.assertEqual(events[1].metadata, {})

        log_status_changed_mock.assert_called_once()
        dispatch_mock.assert_called_once()

    def test_update_status_raises_when_shipment_is_already_delivered(self):
        """Raise ShipmentAlreadyDeliveredException for delivered shipment."""
        shipment = self.create_shipment(status=Shipment.STATUS_DELIVERED)

        with self.assertRaises(ShipmentAlreadyDeliveredException):
            ShippingStatusService.update_status(
                shipment=shipment,
                new_status=Shipment.STATUS_RETURNED,
            )

        shipment.refresh_from_db()
        self.assertEqual(shipment.status, Shipment.STATUS_DELIVERED)
        self.assertEqual(ShipmentEvent.objects.count(), 0)

    def test_update_status_raises_when_shipment_is_already_cancelled(self):
        """Raise ShipmentAlreadyCancelledException for cancelled shipment."""
        shipment = self.create_shipment(status=Shipment.STATUS_CANCELLED)

        with self.assertRaises(ShipmentAlreadyCancelledException):
            ShippingStatusService.update_status(
                shipment=shipment,
                new_status=Shipment.STATUS_PREPARING,
            )

        shipment.refresh_from_db()
        self.assertEqual(shipment.status, Shipment.STATUS_CANCELLED)
        self.assertEqual(ShipmentEvent.objects.count(), 0)

    def test_update_status_raises_for_invalid_transition(self):
        """Raise InvalidShipmentStatusTransitionException for invalid status change."""
        shipment = self.create_shipment(status=Shipment.STATUS_PENDING)

        with self.assertRaises(InvalidShipmentStatusTransitionException):
            ShippingStatusService.update_status(
                shipment=shipment,
                new_status=Shipment.STATUS_SHIPPED,
            )

        shipment.refresh_from_db()
        self.assertEqual(shipment.status, Shipment.STATUS_PENDING)
        self.assertEqual(ShipmentEvent.objects.count(), 0)

    def test_validate_terminal_status_allows_non_terminal_status(self):
        """Allow status validation for non-terminal shipment."""
        shipment = self.create_shipment(status=Shipment.STATUS_IN_TRANSIT)

        ShippingStatusService._validate_terminal_status(shipment=shipment)

    def test_validate_terminal_status_raises_for_delivered_status(self):
        """Raise ShipmentAlreadyDeliveredException for delivered shipment."""
        shipment = self.create_shipment(status=Shipment.STATUS_DELIVERED)

        with self.assertRaises(ShipmentAlreadyDeliveredException):
            ShippingStatusService._validate_terminal_status(shipment=shipment)

    def test_validate_terminal_status_raises_for_cancelled_status(self):
        """Raise ShipmentAlreadyCancelledException for cancelled shipment."""
        shipment = self.create_shipment(status=Shipment.STATUS_CANCELLED)

        with self.assertRaises(ShipmentAlreadyCancelledException):
            ShippingStatusService._validate_terminal_status(shipment=shipment)

    def test_validate_transition_allows_supported_transition(self):
        """Allow a valid shipment status transition."""
        ShippingStatusService._validate_transition(
            current_status=Shipment.STATUS_PENDING,
            new_status=Shipment.STATUS_PREPARING,
        )

    def test_validate_transition_raises_for_unsupported_transition(self):
        """Raise InvalidShipmentStatusTransitionException for unsupported transition."""
        with self.assertRaises(InvalidShipmentStatusTransitionException):
            ShippingStatusService._validate_transition(
                current_status=Shipment.STATUS_PENDING,
                new_status=Shipment.STATUS_DELIVERED,
            )

    def test_update_lifecycle_timestamp_updates_expected_field(self):
        """Update lifecycle timestamp field mapped to the new status."""
        shipment = self.create_shipment(status=Shipment.STATUS_PENDING)

        before_call = timezone.now()
        ShippingStatusService._update_lifecycle_timestamp(
            shipment=shipment,
            new_status=Shipment.STATUS_PREPARING,
        )
        shipment.lifecycle.refresh_from_db()

        self.assertIsNotNone(shipment.lifecycle.preparing_at)
        self.assertGreaterEqual(shipment.lifecycle.preparing_at, before_call)

    def test_update_lifecycle_timestamp_does_nothing_for_unmapped_status(self):
        """Do nothing when new status has no lifecycle field mapping."""
        shipment = self.create_shipment(status=Shipment.STATUS_PENDING)

        ShippingStatusService._update_lifecycle_timestamp(
            shipment=shipment,
            new_status="unknown_status",
        )
        shipment.lifecycle.refresh_from_db()

        self.assertIsNone(shipment.lifecycle.preparing_at)
        self.assertIsNone(shipment.lifecycle.ready_to_ship_at)
        self.assertIsNone(shipment.lifecycle.shipped_at)
        self.assertIsNone(shipment.lifecycle.in_transit_at)
        self.assertIsNone(shipment.lifecycle.out_for_delivery_at)
        self.assertIsNone(shipment.lifecycle.delivered_at)
        self.assertIsNone(shipment.lifecycle.failed_at)
        self.assertIsNone(shipment.lifecycle.returned_at)
        self.assertIsNone(shipment.lifecycle.cancelled_at)

    def test_create_status_change_event_creates_general_and_specific_events(self):
        """Create generic and specific shipment status change events."""
        shipment = self.create_shipment(status=Shipment.STATUS_SHIPPED)
        performed_by = self.create_user(
            email="ops2@company.com",
            user_name="Operations User 2",
            role=User.ROLE_OPERATIONS_STAFF,
        )

        ShippingStatusService._create_status_change_event(
            shipment=shipment,
            previous_status=Shipment.STATUS_SHIPPED,
            new_status=Shipment.STATUS_IN_TRANSIT,
            performed_by=performed_by,
            metadata={"channel": "carrier-webhook"},
        )

        events = list(shipment.events.order_by("created_at"))
        self.assertEqual(len(events), 2)

        self.assertEqual(events[0].event_type, ShipmentEvent.TYPE_STATUS_CHANGED)
        self.assertEqual(
            events[0].metadata,
            {
                "previous_status": Shipment.STATUS_SHIPPED,
                "new_status": Shipment.STATUS_IN_TRANSIT,
                "channel": "carrier-webhook",
            },
        )
        self.assertEqual(events[0].performed_by, performed_by)

        self.assertEqual(events[1].event_type, ShipmentEvent.TYPE_IN_TRANSIT)
        self.assertEqual(events[1].metadata, {"channel": "carrier-webhook"})
        self.assertEqual(events[1].performed_by, performed_by)

    def test_create_status_change_event_creates_only_general_event_for_unmapped_status(self):
        """Create only generic event when status has no specific event mapping."""
        shipment = self.create_shipment(status=Shipment.STATUS_PENDING)

        ShippingStatusService._create_status_change_event(
            shipment=shipment,
            previous_status=Shipment.STATUS_PENDING,
            new_status="custom_status",
            metadata={"source": "manual"},
        )

        events = list(shipment.events.order_by("created_at"))
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, ShipmentEvent.TYPE_STATUS_CHANGED)
        self.assertEqual(
            events[0].metadata,
            {
                "previous_status": Shipment.STATUS_PENDING,
                "new_status": "custom_status",
                "source": "manual",
            },
        )

    def test_allowed_transitions_cover_expected_lifecycle_flow(self):
        """Expose expected allowed transitions for shipment lifecycle."""
        self.assertEqual(
            ShippingStatusService.ALLOWED_TRANSITIONS[Shipment.STATUS_PENDING],
            {
                Shipment.STATUS_PREPARING,
                Shipment.STATUS_CANCELLED,
            },
        )
        self.assertEqual(
            ShippingStatusService.ALLOWED_TRANSITIONS[Shipment.STATUS_PREPARING],
            {
                Shipment.STATUS_READY_TO_SHIP,
                Shipment.STATUS_CANCELLED,
            },
        )
        self.assertEqual(
            ShippingStatusService.ALLOWED_TRANSITIONS[Shipment.STATUS_READY_TO_SHIP],
            {
                Shipment.STATUS_SHIPPED,
                Shipment.STATUS_CANCELLED,
            },
        )
        self.assertEqual(
            ShippingStatusService.ALLOWED_TRANSITIONS[Shipment.STATUS_DELIVERED],
            set(),
        )
        self.assertEqual(
            ShippingStatusService.ALLOWED_TRANSITIONS[Shipment.STATUS_CANCELLED],
            set(),
        )

    def test_event_type_map_contains_expected_specific_events(self):
        """Map shipment statuses to expected specific audit event types."""
        self.assertEqual(
            ShippingStatusService.EVENT_TYPE_MAP[Shipment.STATUS_PREPARING],
            ShipmentEvent.TYPE_PREPARING_STARTED,
        )
        self.assertEqual(
            ShippingStatusService.EVENT_TYPE_MAP[Shipment.STATUS_READY_TO_SHIP],
            ShipmentEvent.TYPE_READY_TO_SHIP,
        )
        self.assertEqual(
            ShippingStatusService.EVENT_TYPE_MAP[Shipment.STATUS_SHIPPED],
            ShipmentEvent.TYPE_SHIPPED,
        )
        self.assertEqual(
            ShippingStatusService.EVENT_TYPE_MAP[Shipment.STATUS_IN_TRANSIT],
            ShipmentEvent.TYPE_IN_TRANSIT,
        )
        self.assertEqual(
            ShippingStatusService.EVENT_TYPE_MAP[Shipment.STATUS_OUT_FOR_DELIVERY],
            ShipmentEvent.TYPE_OUT_FOR_DELIVERY,
        )
        self.assertEqual(
            ShippingStatusService.EVENT_TYPE_MAP[Shipment.STATUS_DELIVERED],
            ShipmentEvent.TYPE_DELIVERED,
        )
        self.assertEqual(
            ShippingStatusService.EVENT_TYPE_MAP[Shipment.STATUS_FAILED],
            ShipmentEvent.TYPE_FAILED,
        )
        self.assertEqual(
            ShippingStatusService.EVENT_TYPE_MAP[Shipment.STATUS_RETURNED],
            ShipmentEvent.TYPE_RETURNED,
        )
        self.assertEqual(
            ShippingStatusService.EVENT_TYPE_MAP[Shipment.STATUS_CANCELLED],
            ShipmentEvent.TYPE_CANCELLED,
        )

    def test_lifecycle_field_map_contains_expected_status_timestamps(self):
        """Map shipment statuses to expected lifecycle timestamp fields."""
        self.assertEqual(
            ShippingStatusService.LIFECYCLE_FIELD_MAP[Shipment.STATUS_PREPARING],
            "preparing_at",
        )
        self.assertEqual(
            ShippingStatusService.LIFECYCLE_FIELD_MAP[Shipment.STATUS_READY_TO_SHIP],
            "ready_to_ship_at",
        )
        self.assertEqual(
            ShippingStatusService.LIFECYCLE_FIELD_MAP[Shipment.STATUS_SHIPPED],
            "shipped_at",
        )
        self.assertEqual(
            ShippingStatusService.LIFECYCLE_FIELD_MAP[Shipment.STATUS_IN_TRANSIT],
            "in_transit_at",
        )
        self.assertEqual(
            ShippingStatusService.LIFECYCLE_FIELD_MAP[Shipment.STATUS_OUT_FOR_DELIVERY],
            "out_for_delivery_at",
        )
        self.assertEqual(
            ShippingStatusService.LIFECYCLE_FIELD_MAP[Shipment.STATUS_DELIVERED],
            "delivered_at",
        )
        self.assertEqual(
            ShippingStatusService.LIFECYCLE_FIELD_MAP[Shipment.STATUS_FAILED],
            "failed_at",
        )
        self.assertEqual(
            ShippingStatusService.LIFECYCLE_FIELD_MAP[Shipment.STATUS_RETURNED],
            "returned_at",
        )
        self.assertEqual(
            ShippingStatusService.LIFECYCLE_FIELD_MAP[Shipment.STATUS_CANCELLED],
            "cancelled_at",
        )