from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ech.orders.models import Order
from ech.shipping.constants.messages import (
    ADDRESS_UPDATE_NOT_ALLOWED,
    SHIPMENT_CANNOT_BE_MODIFIED,
)
from ech.shipping.exceptions import (
    InvalidShippingAddressException,
    ShipmentUpdateNotAllowedException,
)
from ech.shipping.models import (
    Shipment,
    ShipmentAddress,
    ShipmentEvent,
)
from ech.shipping.services.shipping_update_service import ShippingUpdateService


User = get_user_model()


class BaseShippingUpdateFactoryMixin:
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

    def create_address(self, **kwargs):
        shipment = kwargs.pop("shipment")

        data = {
            "shipment": shipment,
            "full_name": "User Tester",
            "address_line": "Av. Paulista, 1000",
            "city": "Sao Paulo",
            "state": "SP",
            "country": "Brazil",
            "postal_code": "01310-100",
            "phone": "11999999999",
            "delivery_instructions": "Leave at concierge.",
        }
        data.update(kwargs)
        return ShipmentAddress.objects.create(**data)


class ShippingUpdateServiceTestCase(BaseShippingUpdateFactoryMixin, TestCase):
    @patch("ech.shipping.services.shipping_update_service.ShippingLogService.log_shipment_updated")
    def test_update_shipment_success_with_shipment_and_address_changes(
        self,
        log_shipment_updated_mock,
    ):
        """Update editable shipment and address fields successfully."""
        shipment = self.create_shipment()
        self.create_address(shipment=shipment)
        performed_by = self.create_user(
            email="ops@company.com",
            user_name="Operations User",
            role=User.ROLE_OPERATIONS_STAFF,
        )

        updated_shipment = ShippingUpdateService.update_shipment(
            shipment=shipment,
            shipment_data={
                "shipping_method": Shipment.METHOD_EXPRESS,
                "carrier_name": "FedEx",
                "tracking_code": "TRACK-UPDATED-001",
                "external_reference": "EXT-UPDATED-001",
                "shipping_cost": Decimal("29.90"),
                "currency": "BRL",
                "estimated_delivery_date": timezone.now().date() + timedelta(days=10),
                "delivered_to_name": "Front Desk",
                "is_return_to_sender": True,
            },
            address_data={
                "full_name": "Raphael Updated",
                "city": "Campinas",
                "phone": "11888888888",
                "delivery_instructions": "Call on arrival.",
            },
            performed_by=performed_by,
            metadata={"source": "unit-test"},
        )

        updated_shipment.refresh_from_db()
        updated_shipment.address.refresh_from_db()

        self.assertEqual(updated_shipment.shipping_method, Shipment.METHOD_EXPRESS)
        self.assertEqual(updated_shipment.carrier_name, "FedEx")
        self.assertEqual(updated_shipment.tracking_code, "TRACK-UPDATED-001")
        self.assertEqual(updated_shipment.external_reference, "EXT-UPDATED-001")
        self.assertEqual(updated_shipment.shipping_cost, Decimal("29.90"))
        self.assertEqual(updated_shipment.currency, "BRL")
        self.assertEqual(updated_shipment.delivered_to_name, "Front Desk")
        self.assertTrue(updated_shipment.is_return_to_sender)

        self.assertEqual(updated_shipment.address.full_name, "Raphael Updated")
        self.assertEqual(updated_shipment.address.city, "Campinas")
        self.assertEqual(updated_shipment.address.phone, "11888888888")
        self.assertEqual(
            updated_shipment.address.delivery_instructions,
            "Call on arrival.",
        )

        event = ShipmentEvent.objects.get(shipment=updated_shipment)
        self.assertEqual(event.event_type, ShipmentEvent.TYPE_UPDATED)
        self.assertEqual(event.performed_by, performed_by)
        self.assertEqual(
            event.metadata,
            {
                "shipment_changed_fields": [
                    "shipping_method",
                    "carrier_name",
                    "tracking_code",
                    "external_reference",
                    "shipping_cost",
                    "currency",
                    "estimated_delivery_date",
                    "delivered_to_name",
                    "is_return_to_sender",
                ],
                "address_changed_fields": [
                    "full_name",
                    "city",
                    "phone",
                    "delivery_instructions",
                ],
                "source": "unit-test",
            },
        )

        log_shipment_updated_mock.assert_called_once_with(
            shipment=updated_shipment,
            shipment_changed_fields=[
                "shipping_method",
                "carrier_name",
                "tracking_code",
                "external_reference",
                "shipping_cost",
                "currency",
                "estimated_delivery_date",
                "delivered_to_name",
                "is_return_to_sender",
            ],
            address_changed_fields=[
                "full_name",
                "city",
                "phone",
                "delivery_instructions",
            ],
            performed_by=performed_by,
        )

    @patch("ech.shipping.services.shipping_update_service.ShippingLogService.log_shipment_updated")
    def test_update_shipment_success_with_only_shipment_changes(
        self,
        log_shipment_updated_mock,
    ):
        """Update only shipment fields when no address payload is provided."""
        shipment = self.create_shipment()
        self.create_address(shipment=shipment)

        updated_shipment = ShippingUpdateService.update_shipment(
            shipment=shipment,
            shipment_data={
                "carrier_name": "UPS",
                "tracking_code": "TRACK-UPS-001",
            },
        )

        updated_shipment.refresh_from_db()

        self.assertEqual(updated_shipment.carrier_name, "UPS")
        self.assertEqual(updated_shipment.tracking_code, "TRACK-UPS-001")

        event = ShipmentEvent.objects.get(shipment=updated_shipment)
        self.assertEqual(
            event.metadata,
            {
                "shipment_changed_fields": ["carrier_name", "tracking_code"],
                "address_changed_fields": [],
            },
        )

        log_shipment_updated_mock.assert_called_once_with(
            shipment=updated_shipment,
            shipment_changed_fields=["carrier_name", "tracking_code"],
            address_changed_fields=[],
            performed_by=None,
        )

    @patch("ech.shipping.services.shipping_update_service.ShippingLogService.log_shipment_updated")
    def test_update_shipment_success_with_only_address_changes(
        self,
        log_shipment_updated_mock,
    ):
        """Update only address fields when shipment fields are not changed."""
        shipment = self.create_shipment()
        self.create_address(shipment=shipment)

        updated_shipment = ShippingUpdateService.update_shipment(
            shipment=shipment,
            address_data={
                "city": "Rio de Janeiro",
                "state": "RJ",
            },
        )

        updated_shipment.address.refresh_from_db()

        self.assertEqual(updated_shipment.address.city, "Rio de Janeiro")
        self.assertEqual(updated_shipment.address.state, "RJ")

        event = ShipmentEvent.objects.get(shipment=updated_shipment)
        self.assertEqual(
            event.metadata,
            {
                "shipment_changed_fields": [],
                "address_changed_fields": ["city", "state"],
            },
        )

        log_shipment_updated_mock.assert_called_once_with(
            shipment=updated_shipment,
            shipment_changed_fields=[],
            address_changed_fields=["city", "state"],
            performed_by=None,
        )

    @patch("ech.shipping.services.shipping_update_service.ShippingLogService.log_shipment_updated")
    def test_update_shipment_ignores_non_editable_fields(
        self,
        log_shipment_updated_mock,
    ):
        """Ignore non-editable shipment and address fields during update."""
        shipment = self.create_shipment(status=Shipment.STATUS_PENDING)
        self.create_address(shipment=shipment)

        updated_shipment = ShippingUpdateService.update_shipment(
            shipment=shipment,
            shipment_data={
                "status": Shipment.STATUS_SHIPPED,
                "customer": self.create_user(),
                "carrier_name": "Correios",
            },
            address_data={
                "created_at": timezone.now(),
                "country": "Argentina",
            },
        )

        updated_shipment.refresh_from_db()
        updated_shipment.address.refresh_from_db()

        self.assertEqual(updated_shipment.status, Shipment.STATUS_PENDING)
        self.assertEqual(updated_shipment.carrier_name, "Correios")
        self.assertEqual(updated_shipment.address.country, "Argentina")

        event = ShipmentEvent.objects.get(shipment=updated_shipment)
        self.assertEqual(
            event.metadata,
            {
                "shipment_changed_fields": ["carrier_name"],
                "address_changed_fields": ["country"],
            },
        )

        log_shipment_updated_mock.assert_called_once()

    @patch("ech.shipping.services.shipping_update_service.ShippingLogService.log_shipment_updated")
    def test_update_shipment_does_not_create_event_or_log_when_nothing_changes(
        self,
        log_shipment_updated_mock,
    ):
        """Do not create event or log when update payload changes nothing."""
        shipment = self.create_shipment(
            carrier_name="DHL",
            tracking_code="TRACK-SAME-001",
        )
        self.create_address(
            shipment=shipment,
            city="Sao Paulo",
            country="Brazil",
        )

        updated_shipment = ShippingUpdateService.update_shipment(
            shipment=shipment,
            shipment_data={
                "carrier_name": "DHL",
                "tracking_code": "TRACK-SAME-001",
            },
            address_data={
                "city": "Sao Paulo",
                "country": "Brazil",
            },
        )

        self.assertEqual(updated_shipment, shipment)
        self.assertEqual(ShipmentEvent.objects.count(), 0)
        log_shipment_updated_mock.assert_not_called()

    def test_update_shipment_raises_exception_for_non_editable_status(self):
        """Raise ShipmentUpdateNotAllowedException for non-editable shipment status."""
        shipment = self.create_shipment(status=Shipment.STATUS_DELIVERED)
        self.create_address(shipment=shipment)

        with self.assertRaises(ShipmentUpdateNotAllowedException) as context:
            ShippingUpdateService.update_shipment(
                shipment=shipment,
                shipment_data={"carrier_name": "FedEx"},
            )

        self.assertEqual(str(context.exception), SHIPMENT_CANNOT_BE_MODIFIED)
        self.assertEqual(ShipmentEvent.objects.count(), 0)

    def test_update_shipment_raises_exception_when_address_is_locked(self):
        """Raise ShipmentUpdateNotAllowedException when address update is locked."""
        shipment = self.create_shipment(status=Shipment.STATUS_SHIPPED)
        self.create_address(shipment=shipment)

        with self.assertRaises(ShipmentUpdateNotAllowedException) as context:
            ShippingUpdateService.update_shipment(
                shipment=shipment,
                address_data={"city": "Curitiba"},
            )

        self.assertEqual(str(context.exception), ADDRESS_UPDATE_NOT_ALLOWED)
        self.assertEqual(ShipmentEvent.objects.count(), 0)

    def test_update_shipment_raises_exception_for_invalid_address_payload(self):
        """Raise InvalidShippingAddressException for invalid required address fields."""
        shipment = self.create_shipment(status=Shipment.STATUS_PENDING)
        self.create_address(shipment=shipment)

        with self.assertRaises(InvalidShippingAddressException) as context:
            ShippingUpdateService.update_shipment(
                shipment=shipment,
                address_data={
                    "full_name": "",
                    "city": None,
                },
            )

        self.assertEqual(
            str(context.exception),
            "Invalid required address fields: full_name, city.",
        )
        self.assertEqual(ShipmentEvent.objects.count(), 0)

    def test_validate_shipment_can_be_modified_allows_editable_status(self):
        """Allow shipment updates for editable statuses."""
        shipment = self.create_shipment(status=Shipment.STATUS_PENDING)

        ShippingUpdateService._validate_shipment_can_be_modified(
            shipment=shipment
        )

    def test_validate_shipment_can_be_modified_raises_for_non_editable_status(self):
        """Raise ShipmentUpdateNotAllowedException for delivered shipment."""
        shipment = self.create_shipment(status=Shipment.STATUS_CANCELLED)

        with self.assertRaises(ShipmentUpdateNotAllowedException) as context:
            ShippingUpdateService._validate_shipment_can_be_modified(
                shipment=shipment
            )

        self.assertEqual(str(context.exception), SHIPMENT_CANNOT_BE_MODIFIED)

    def test_apply_shipment_updates_returns_only_changed_editable_fields(self):
        """Apply shipment updates and return only changed editable fields."""
        shipment = self.create_shipment(
            carrier_name="DHL",
            currency="USD",
        )

        changed_fields = ShippingUpdateService._apply_shipment_updates(
            shipment=shipment,
            shipment_data={
                "carrier_name": "FedEx",
                "currency": "USD",
                "status": Shipment.STATUS_SHIPPED,
            },
        )

        self.assertEqual(changed_fields, ["carrier_name"])
        self.assertEqual(shipment.carrier_name, "FedEx")
        self.assertEqual(shipment.status, Shipment.STATUS_PENDING)

    def test_apply_address_updates_returns_only_changed_editable_fields(self):
        """Apply address updates and return only changed editable fields."""
        shipment = self.create_shipment(status=Shipment.STATUS_PENDING)
        self.create_address(
            shipment=shipment,
            city="Sao Paulo",
            state="SP",
        )

        changed_fields = ShippingUpdateService._apply_address_updates(
            shipment=shipment,
            address_data={
                "city": "Campinas",
                "state": "SP",
                "created_at": timezone.now(),
            },
        )

        self.assertEqual(changed_fields, ["city"])
        self.assertEqual(shipment.address.city, "Campinas")
        self.assertEqual(shipment.address.state, "SP")

    def test_apply_address_updates_returns_empty_list_when_payload_is_empty(self):
        """Return empty list when no address payload is provided."""
        shipment = self.create_shipment(status=Shipment.STATUS_PENDING)
        self.create_address(shipment=shipment)

        changed_fields = ShippingUpdateService._apply_address_updates(
            shipment=shipment,
            address_data={},
        )

        self.assertEqual(changed_fields, [])

    def test_validate_address_can_be_updated_allows_pending_shipment(self):
        """Allow address updates when shipment status is editable."""
        shipment = self.create_shipment(status=Shipment.STATUS_PENDING)

        ShippingUpdateService._validate_address_can_be_updated(
            shipment=shipment
        )

    def test_validate_address_can_be_updated_raises_for_locked_status(self):
        """Raise ShipmentUpdateNotAllowedException for locked address status."""
        shipment = self.create_shipment(status=Shipment.STATUS_IN_TRANSIT)

        with self.assertRaises(ShipmentUpdateNotAllowedException) as context:
            ShippingUpdateService._validate_address_can_be_updated(
                shipment=shipment
            )

        self.assertEqual(str(context.exception), ADDRESS_UPDATE_NOT_ALLOWED)

    def test_validate_address_payload_accepts_valid_partial_payload(self):
        """Accept valid partial address payload updates."""
        ShippingUpdateService._validate_address_payload(
            address_data={
                "city": "Campinas",
                "phone": "",
            }
        )

    def test_validate_address_payload_raises_for_invalid_required_fields(self):
        """Raise InvalidShippingAddressException for invalid provided required fields."""
        with self.assertRaises(InvalidShippingAddressException) as context:
            ShippingUpdateService._validate_address_payload(
                address_data={
                    "address_line": "",
                    "postal_code": None,
                }
            )

        message = str(context.exception)

        self.assertIn("Invalid required address fields:", message)
        self.assertIn("address_line", message)
        self.assertIn("postal_code", message)

    def test_create_update_event_creates_expected_audit_event(self):
        """Create shipment update event with changed field metadata."""
        shipment = self.create_shipment()
        performed_by = self.create_user(
            email="ops2@company.com",
            user_name="Operations User 2",
            role=User.ROLE_OPERATIONS_STAFF,
        )

        ShippingUpdateService._create_update_event(
            shipment=shipment,
            shipment_changed_fields=["carrier_name", "tracking_code"],
            address_changed_fields=["city"],
            performed_by=performed_by,
            metadata={"source": "manual-review"},
        )

        event = ShipmentEvent.objects.get(shipment=shipment)

        self.assertEqual(event.event_type, ShipmentEvent.TYPE_UPDATED)
        self.assertEqual(event.performed_by, performed_by)
        self.assertEqual(
            event.metadata,
            {
                "shipment_changed_fields": ["carrier_name", "tracking_code"],
                "address_changed_fields": ["city"],
                "source": "manual-review",
            },
        )