from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ech.orders.models import Order
from ech.shipping.exceptions import (
    InvalidTrackingEventException,
)
from ech.shipping.models import (
    Shipment,
    ShipmentEvent,
    ShipmentTrackingUpdate,
)
from ech.shipping.services.shipping_tracking_service import (
    ShippingTrackingService,
)


User = get_user_model()


class BaseShippingTrackingFactoryMixin:
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
            "external_reference": "EXT-001",
            "shipping_cost": Decimal("19.90"),
            "currency": "USD",
            "estimated_delivery_date": timezone.now().date() + timedelta(days=5),
            "delivered_to_name": "",
            "is_return_to_sender": False,
        }
        data.update(kwargs)
        return Shipment.objects.create(**data)


class ShippingTrackingServiceTestCase(
    BaseShippingTrackingFactoryMixin,
    TestCase,
):
    @patch(
        "ech.shipping.services.shipping_tracking_service."
        "ShippingLogService.log_tracking_updated"
    )
    @patch(
        "ech.shipping.services.shipping_tracking_service."
        "ShippingStatusService.update_status"
    )
    def test_register_tracking_update_success_with_metadata_changes_and_status_update(
        self,
        update_status_mock,
        log_tracking_updated_mock,
    ):
        """Register tracking update successfully with metadata and status sync."""
        shipment = self.create_shipment(
            status=Shipment.STATUS_PREPARING,
            tracking_code="TRACK-OLD-001",
            carrier_name="Old Carrier",
            external_reference="EXT-OLD-001",
        )
        performed_by = self.create_user(
            email="ops@company.com",
            user_name="Operations User",
            role=User.ROLE_OPERATIONS_STAFF,
        )
        event_at = timezone.now()

        tracking_update = ShippingTrackingService.register_tracking_update(
            shipment=shipment,
            description="Package departed from facility.",
            event_at=event_at,
            status=Shipment.STATUS_SHIPPED,
            location="Sao Paulo Hub",
            raw_payload={"carrier_status": "departed"},
            tracking_code="TRACK-NEW-001",
            carrier_name="DHL Express",
            external_reference="EXT-NEW-001",
            performed_by=performed_by,
        )

        shipment.refresh_from_db()

        self.assertEqual(ShipmentTrackingUpdate.objects.count(), 1)
        self.assertEqual(ShipmentEvent.objects.count(), 1)

        self.assertEqual(tracking_update.shipment, shipment)
        self.assertEqual(tracking_update.status, Shipment.STATUS_SHIPPED)
        self.assertEqual(tracking_update.location, "Sao Paulo Hub")
        self.assertEqual(
            tracking_update.description,
            "Package departed from facility.",
        )
        self.assertEqual(
            tracking_update.raw_payload,
            {"carrier_status": "departed"},
        )
        self.assertEqual(tracking_update.event_at, event_at)

        self.assertEqual(shipment.tracking_code, "TRACK-NEW-001")
        self.assertEqual(shipment.carrier_name, "DHL Express")
        self.assertEqual(shipment.external_reference, "EXT-NEW-001")

        event = ShipmentEvent.objects.get()
        self.assertEqual(event.event_type, ShipmentEvent.TYPE_TRACKING_UPDATED)
        self.assertEqual(event.performed_by, performed_by)
        self.assertEqual(
            event.metadata,
            {
                "tracking_update_id": tracking_update.id,
                "status": Shipment.STATUS_SHIPPED,
                "location": "Sao Paulo Hub",
                "description": "Package departed from facility.",
                "event_at": event_at.isoformat(),
                "tracking_code": "TRACK-NEW-001",
                "carrier_name": "DHL Express",
                "external_reference": "EXT-NEW-001",
            },
        )

        update_status_mock.assert_called_once_with(
            shipment=shipment,
            new_status=Shipment.STATUS_SHIPPED,
            performed_by=performed_by,
            metadata={
                "source": "tracking_update",
                "tracking_update_id": tracking_update.id,
                "tracking_description": "Package departed from facility.",
            },
        )

        log_tracking_updated_mock.assert_called_once_with(
            shipment=shipment,
            tracking_update=tracking_update,
            performed_by=performed_by,
        )

    @patch(
        "ech.shipping.services.shipping_tracking_service."
        "ShippingLogService.log_tracking_updated"
    )
    @patch(
        "ech.shipping.services.shipping_tracking_service."
        "ShippingStatusService.update_status"
    )
    def test_register_tracking_update_success_without_status_or_metadata_changes(
        self,
        update_status_mock,
        log_tracking_updated_mock,
    ):
        """Register tracking update without shipment metadata or status changes."""
        shipment = self.create_shipment(
            status=Shipment.STATUS_IN_TRANSIT,
            tracking_code="TRACK-STABLE-001",
            carrier_name="DHL",
            external_reference="EXT-STABLE-001",
        )
        event_at = timezone.now()

        tracking_update = ShippingTrackingService.register_tracking_update(
            shipment=shipment,
            description="Package scanned at transit facility.",
            event_at=event_at,
            status=Shipment.STATUS_IN_TRANSIT,
            location="Curitiba",
        )

        shipment.refresh_from_db()

        self.assertEqual(tracking_update.status, Shipment.STATUS_IN_TRANSIT)
        self.assertEqual(shipment.tracking_code, "TRACK-STABLE-001")
        self.assertEqual(shipment.carrier_name, "DHL")
        self.assertEqual(shipment.external_reference, "EXT-STABLE-001")

        event = ShipmentEvent.objects.get()
        self.assertEqual(
            event.metadata,
            {
                "tracking_update_id": tracking_update.id,
                "status": Shipment.STATUS_IN_TRANSIT,
                "location": "Curitiba",
                "description": "Package scanned at transit facility.",
                "event_at": event_at.isoformat(),
                "tracking_code": "TRACK-STABLE-001",
                "carrier_name": "DHL",
                "external_reference": "EXT-STABLE-001",
            },
        )

        update_status_mock.assert_not_called()
        log_tracking_updated_mock.assert_called_once_with(
            shipment=shipment,
            tracking_update=tracking_update,
            performed_by=None,
        )

    @patch(
        "ech.shipping.services.shipping_tracking_service."
        "ShippingLogService.log_tracking_updated"
    )
    @patch(
        "ech.shipping.services.shipping_tracking_service."
        "ShippingStatusService.update_status"
    )
    def test_register_tracking_update_success_with_blank_optional_values(
        self,
        update_status_mock,
        log_tracking_updated_mock,
    ):
        """Register tracking update successfully with blank optional values."""
        shipment = self.create_shipment(
            status=Shipment.STATUS_PENDING,
            tracking_code=None,
            carrier_name="",
            external_reference=None,
        )
        event_at = timezone.now()

        tracking_update = ShippingTrackingService.register_tracking_update(
            shipment=shipment,
            description="Tracking initialized.",
            event_at=event_at,
            location="",
            raw_payload=None,
        )

        shipment.refresh_from_db()

        self.assertEqual(tracking_update.status, "")
        self.assertEqual(tracking_update.location, "")
        self.assertIsNone(tracking_update.raw_payload)

        event = ShipmentEvent.objects.get()
        self.assertEqual(
            event.metadata,
            {
                "tracking_update_id": tracking_update.id,
                "status": None,
                "location": "",
                "description": "Tracking initialized.",
                "event_at": event_at.isoformat(),
                "tracking_code": None,
                "carrier_name": "",
                "external_reference": None,
            },
        )

        update_status_mock.assert_not_called()
        log_tracking_updated_mock.assert_called_once()

    @patch(
        "ech.shipping.services.shipping_tracking_service."
        "ShippingLogService.log_tracking_updated"
    )
    @patch(
        "ech.shipping.services.shipping_tracking_service."
        "ShippingStatusService.update_status"
    )
    def test_register_tracking_update_does_not_save_shipment_when_metadata_did_not_change(
        self,
        update_status_mock,
        log_tracking_updated_mock,
    ):
        """Do not save shipment metadata when provided values are unchanged."""
        shipment = self.create_shipment(
            status=Shipment.STATUS_PENDING,
            tracking_code="TRACK-SAME-001",
            carrier_name="DHL",
            external_reference="EXT-SAME-001",
        )
        original_updated_at = shipment.updated_at
        event_at = timezone.now()

        tracking_update = ShippingTrackingService.register_tracking_update(
            shipment=shipment,
            description="Package label confirmed.",
            event_at=event_at,
            tracking_code="TRACK-SAME-001",
            carrier_name="DHL",
            external_reference="EXT-SAME-001",
        )

        shipment.refresh_from_db()

        self.assertEqual(shipment.updated_at, original_updated_at)
        self.assertEqual(tracking_update.description, "Package label confirmed.")
        update_status_mock.assert_not_called()
        log_tracking_updated_mock.assert_called_once()

    def test_register_tracking_update_raises_for_missing_description(self):
        """Raise InvalidTrackingEventException when description is missing."""
        shipment = self.create_shipment()

        with self.assertRaises(InvalidTrackingEventException) as context:
            ShippingTrackingService.register_tracking_update(
                shipment=shipment,
                description="",
                event_at=timezone.now(),
            )

        self.assertEqual(
            str(context.exception),
            "Tracking description is required.",
        )
        self.assertEqual(ShipmentTrackingUpdate.objects.count(), 0)
        self.assertEqual(ShipmentEvent.objects.count(), 0)

    def test_register_tracking_update_raises_for_missing_event_at(self):
        """Raise InvalidTrackingEventException when event timestamp is missing."""
        shipment = self.create_shipment()

        with self.assertRaises(InvalidTrackingEventException) as context:
            ShippingTrackingService.register_tracking_update(
                shipment=shipment,
                description="Package registered.",
                event_at=None,
            )

        self.assertEqual(
            str(context.exception),
            "Tracking event timestamp is required.",
        )
        self.assertEqual(ShipmentTrackingUpdate.objects.count(), 0)
        self.assertEqual(ShipmentEvent.objects.count(), 0)

    def test_register_tracking_update_raises_for_invalid_status(self):
        """Raise InvalidTrackingEventException for unsupported tracking status."""
        shipment = self.create_shipment()

        with self.assertRaises(InvalidTrackingEventException):
            ShippingTrackingService.register_tracking_update(
                shipment=shipment,
                description="Invalid carrier event.",
                event_at=timezone.now(),
                status="unknown_status",
            )

        self.assertEqual(ShipmentTrackingUpdate.objects.count(), 0)
        self.assertEqual(ShipmentEvent.objects.count(), 0)

    def test_validate_tracking_data_accepts_valid_payload(self):
        """Accept tracking payload with valid required fields and status."""
        ShippingTrackingService._validate_tracking_data(
            description="Package processed.",
            event_at=timezone.now(),
            status=Shipment.STATUS_SHIPPED,
        )

    def test_validate_tracking_data_accepts_missing_status(self):
        """Accept tracking payload without optional status."""
        ShippingTrackingService._validate_tracking_data(
            description="Package processed.",
            event_at=timezone.now(),
            status=None,
        )

    def test_validate_tracking_data_raises_for_missing_description(self):
        """Raise InvalidTrackingEventException for blank tracking description."""
        with self.assertRaises(InvalidTrackingEventException) as context:
            ShippingTrackingService._validate_tracking_data(
                description=None,
                event_at=timezone.now(),
            )

        self.assertEqual(
            str(context.exception),
            "Tracking description is required.",
        )

    def test_validate_tracking_data_raises_for_missing_event_timestamp(self):
        """Raise InvalidTrackingEventException for missing tracking timestamp."""
        with self.assertRaises(InvalidTrackingEventException) as context:
            ShippingTrackingService._validate_tracking_data(
                description="Package processed.",
                event_at=None,
            )

        self.assertEqual(
            str(context.exception),
            "Tracking event timestamp is required.",
        )

    def test_validate_tracking_data_raises_for_invalid_status(self):
        """Raise InvalidTrackingEventException for invalid tracking status."""
        with self.assertRaises(InvalidTrackingEventException):
            ShippingTrackingService._validate_tracking_data(
                description="Package processed.",
                event_at=timezone.now(),
                status="invalid_status",
            )

    def test_update_shipment_tracking_metadata_updates_changed_fields(self):
        """Update shipment tracking metadata only when new values differ."""
        shipment = self.create_shipment(
            tracking_code="TRACK-OLD-001",
            carrier_name="Old Carrier",
            external_reference="EXT-OLD-001",
        )

        changed = ShippingTrackingService._update_shipment_tracking_metadata(
            shipment=shipment,
            tracking_code="TRACK-NEW-001",
            carrier_name="New Carrier",
            external_reference="EXT-NEW-001",
        )

        self.assertTrue(changed)
        self.assertEqual(shipment.tracking_code, "TRACK-NEW-001")
        self.assertEqual(shipment.carrier_name, "New Carrier")
        self.assertEqual(shipment.external_reference, "EXT-NEW-001")

    def test_update_shipment_tracking_metadata_returns_false_when_nothing_changed(self):
        """Return false when shipment tracking metadata remains unchanged."""
        shipment = self.create_shipment(
            tracking_code="TRACK-STABLE-001",
            carrier_name="Stable Carrier",
            external_reference="EXT-STABLE-001",
        )

        changed = ShippingTrackingService._update_shipment_tracking_metadata(
            shipment=shipment,
            tracking_code="TRACK-STABLE-001",
            carrier_name="Stable Carrier",
            external_reference="EXT-STABLE-001",
        )

        self.assertFalse(changed)
        self.assertEqual(shipment.tracking_code, "TRACK-STABLE-001")
        self.assertEqual(shipment.carrier_name, "Stable Carrier")
        self.assertEqual(shipment.external_reference, "EXT-STABLE-001")

    def test_update_shipment_tracking_metadata_ignores_blank_optional_inputs(self):
        """Ignore blank metadata inputs and keep existing shipment values."""
        shipment = self.create_shipment(
            tracking_code="TRACK-KEEP-001",
            carrier_name="Keep Carrier",
            external_reference="EXT-KEEP-001",
        )

        changed = ShippingTrackingService._update_shipment_tracking_metadata(
            shipment=shipment,
            tracking_code=None,
            carrier_name="",
            external_reference=None,
        )

        self.assertFalse(changed)
        self.assertEqual(shipment.tracking_code, "TRACK-KEEP-001")
        self.assertEqual(shipment.carrier_name, "Keep Carrier")
        self.assertEqual(shipment.external_reference, "EXT-KEEP-001")

    def test_tracking_status_map_contains_expected_statuses(self):
        """Expose expected tracking status map values."""
        self.assertEqual(
            ShippingTrackingService.TRACKING_STATUS_MAP,
            {
                Shipment.STATUS_PREPARING: Shipment.STATUS_PREPARING,
                Shipment.STATUS_READY_TO_SHIP: Shipment.STATUS_READY_TO_SHIP,
                Shipment.STATUS_SHIPPED: Shipment.STATUS_SHIPPED,
                Shipment.STATUS_IN_TRANSIT: Shipment.STATUS_IN_TRANSIT,
                Shipment.STATUS_OUT_FOR_DELIVERY: Shipment.STATUS_OUT_FOR_DELIVERY,
                Shipment.STATUS_DELIVERED: Shipment.STATUS_DELIVERED,
                Shipment.STATUS_FAILED: Shipment.STATUS_FAILED,
                Shipment.STATUS_RETURNED: Shipment.STATUS_RETURNED,
            },
        )