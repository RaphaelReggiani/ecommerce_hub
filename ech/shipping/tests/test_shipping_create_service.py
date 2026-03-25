from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ech.orders.models import Order
from ech.shipping.exceptions import (
    InvalidShippingAddressException,
    ShipmentAlreadyExistsException,
)
from ech.shipping.models import (
    Shipment,
    ShipmentAddress,
    ShipmentEvent,
    ShipmentLifecycle,
)
from ech.shipping.services.shipping_creation_service import ShippingCreationService


User = get_user_model()


class BaseShippingCreationFactoryMixin:
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

    def get_address_data(self, **kwargs):
        data = {
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
        return data


class ShippingCreationServiceTestCase(BaseShippingCreationFactoryMixin, TestCase):
    @patch("ech.shipping.services.shipping_creation_service.DomainEventDispatcher.dispatch")
    @patch("ech.shipping.services.shipping_creation_service.ShippingLogService.log_shipment_created")
    @patch("ech.shipping.services.shipping_creation_service.ShipmentCreatedEvent")
    def test_create_shipment_success(
        self,
        shipment_created_event_mock,
        log_shipment_created_mock,
        dispatch_mock,
    ):
        """Create shipment aggregate and related records successfully."""
        customer = self.create_user()
        performed_by = self.create_user(
            email="ops@company.com",
            user_name="Operations User",
            role=User.ROLE_OPERATIONS_STAFF,
        )
        order = self.create_order(customer=customer)
        estimated_delivery_date = timezone.now().date() + timedelta(days=5)
        address_data = self.get_address_data()

        shipment = ShippingCreationService.create_shipment(
            order=order,
            customer=customer,
            shipping_method=Shipment.METHOD_EXPRESS,
            address_data=address_data,
            shipping_cost=Decimal("25.50"),
            currency="USD",
            carrier_name="DHL",
            tracking_code="TRACK-CREATE-001",
            external_reference="EXT-CREATE-001",
            estimated_delivery_date=estimated_delivery_date,
            idempotency_key=uuid.uuid4(),
            performed_by=performed_by,
        )

        self.assertEqual(Shipment.objects.count(), 1)
        self.assertEqual(ShipmentAddress.objects.count(), 1)
        self.assertEqual(ShipmentLifecycle.objects.count(), 1)
        self.assertEqual(ShipmentEvent.objects.count(), 1)

        self.assertEqual(shipment.order, order)
        self.assertEqual(shipment.customer, customer)
        self.assertEqual(shipment.status, Shipment.STATUS_PENDING)
        self.assertEqual(shipment.shipping_method, Shipment.METHOD_EXPRESS)
        self.assertEqual(shipment.shipping_cost, Decimal("25.50"))
        self.assertEqual(shipment.currency, "USD")
        self.assertEqual(shipment.carrier_name, "DHL")
        self.assertEqual(shipment.tracking_code, "TRACK-CREATE-001")
        self.assertEqual(shipment.external_reference, "EXT-CREATE-001")
        self.assertEqual(shipment.estimated_delivery_date, estimated_delivery_date)

        address = shipment.address
        self.assertEqual(address.full_name, address_data["full_name"])
        self.assertEqual(address.address_line, address_data["address_line"])
        self.assertEqual(address.city, address_data["city"])
        self.assertEqual(address.state, address_data["state"])
        self.assertEqual(address.country, address_data["country"])
        self.assertEqual(address.postal_code, address_data["postal_code"])
        self.assertEqual(address.phone, address_data["phone"])
        self.assertEqual(
            address.delivery_instructions,
            address_data["delivery_instructions"],
        )

        self.assertIsNotNone(shipment.lifecycle)

        event = shipment.events.get()
        self.assertEqual(event.event_type, ShipmentEvent.TYPE_CREATED)
        self.assertEqual(event.performed_by, performed_by)
        self.assertEqual(
            event.metadata,
            {
                "order_id": str(order.id),
                "customer_id": str(customer.id),
                "shipping_method": Shipment.METHOD_EXPRESS,
                "tracking_code": "TRACK-CREATE-001",
                "carrier_name": "DHL",
                "estimated_delivery_date": estimated_delivery_date.isoformat(),
            },
        )

        log_shipment_created_mock.assert_called_once_with(
            shipment=shipment,
            performed_by=performed_by,
        )

        shipment_created_event_mock.assert_called_once_with(
            shipment_id=shipment.id,
            order_id=order.id,
            customer_id=customer.id,
            performed_by_id=performed_by.id,
        )
        dispatch_mock.assert_called_once_with(
            shipment_created_event_mock.return_value
        )

    @patch("ech.shipping.services.shipping_creation_service.DomainEventDispatcher.dispatch")
    @patch("ech.shipping.services.shipping_creation_service.ShippingLogService.log_shipment_created")
    @patch("ech.shipping.services.shipping_creation_service.ShipmentCreatedEvent")
    def test_create_shipment_success_with_optional_fields_omitted(
        self,
        shipment_created_event_mock,
        log_shipment_created_mock,
        dispatch_mock,
    ):
        """Create shipment successfully when optional fields are omitted."""
        customer = self.create_user()
        order = self.create_order(customer=customer)
        address_data = self.get_address_data()

        shipment = ShippingCreationService.create_shipment(
            order=order,
            customer=customer,
            shipping_method=Shipment.METHOD_STANDARD,
            address_data=address_data,
        )

        self.assertEqual(shipment.status, Shipment.STATUS_PENDING)
        self.assertEqual(shipment.shipping_method, Shipment.METHOD_STANDARD)
        self.assertEqual(shipment.shipping_cost, 0)
        self.assertEqual(shipment.currency, "USD")
        self.assertEqual(shipment.carrier_name, "")
        self.assertIsNone(shipment.tracking_code)
        self.assertIsNone(shipment.external_reference)
        self.assertIsNone(shipment.estimated_delivery_date)
        self.assertIsNone(shipment.idempotency_key)

        address = shipment.address
        self.assertEqual(address.phone, address_data["phone"])
        self.assertEqual(
            address.delivery_instructions,
            address_data["delivery_instructions"],
        )

        event = shipment.events.get()
        self.assertEqual(
            event.metadata,
            {
                "order_id": str(order.id),
                "customer_id": str(customer.id),
                "shipping_method": Shipment.METHOD_STANDARD,
                "tracking_code": None,
                "carrier_name": "",
                "estimated_delivery_date": None,
            },
        )

        log_shipment_created_mock.assert_called_once_with(
            shipment=shipment,
            performed_by=None,
        )

        shipment_created_event_mock.assert_called_once_with(
            shipment_id=shipment.id,
            order_id=order.id,
            customer_id=customer.id,
            performed_by_id=None,
        )
        dispatch_mock.assert_called_once_with(
            shipment_created_event_mock.return_value
        )

    @patch("ech.shipping.services.shipping_creation_service.DomainEventDispatcher.dispatch")
    @patch("ech.shipping.services.shipping_creation_service.ShippingLogService.log_shipment_created")
    def test_create_shipment_uses_default_blank_address_optional_fields(
        self,
        log_shipment_created_mock,
        dispatch_mock,
    ):
        """Default missing optional address fields to blank values."""
        customer = self.create_user()
        order = self.create_order(customer=customer)
        address_data = self.get_address_data()
        address_data.pop("phone")
        address_data.pop("delivery_instructions")

        shipment = ShippingCreationService.create_shipment(
            order=order,
            customer=customer,
            shipping_method=Shipment.METHOD_STANDARD,
            address_data=address_data,
        )

        address = shipment.address

        self.assertEqual(address.phone, "")
        self.assertEqual(address.delivery_instructions, "")
        log_shipment_created_mock.assert_called_once()
        dispatch_mock.assert_called_once()

    def test_create_shipment_raises_exception_when_shipment_already_exists(self):
        """Raise ShipmentAlreadyExistsException when order already has shipment."""
        customer = self.create_user()
        order = self.create_order(customer=customer)
        self.create_existing_shipment(order=order, customer=customer)

        with self.assertRaises(ShipmentAlreadyExistsException):
            ShippingCreationService.create_shipment(
                order=order,
                customer=customer,
                shipping_method=Shipment.METHOD_STANDARD,
                address_data=self.get_address_data(),
            )

    @patch("ech.shipping.services.shipping_creation_service.DomainEventDispatcher.dispatch")
    @patch("ech.shipping.services.shipping_creation_service.ShippingLogService.log_shipment_created")
    def test_create_shipment_does_not_create_records_when_shipment_already_exists(
        self,
        log_shipment_created_mock,
        dispatch_mock,
    ):
        """Do not create related records when shipment already exists."""
        customer = self.create_user()
        order = self.create_order(customer=customer)
        self.create_existing_shipment(order=order, customer=customer)

        initial_shipment_count = Shipment.objects.count()
        initial_address_count = ShipmentAddress.objects.count()
        initial_lifecycle_count = ShipmentLifecycle.objects.count()
        initial_event_count = ShipmentEvent.objects.count()

        with self.assertRaises(ShipmentAlreadyExistsException):
            ShippingCreationService.create_shipment(
                order=order,
                customer=customer,
                shipping_method=Shipment.METHOD_STANDARD,
                address_data=self.get_address_data(),
            )

        self.assertEqual(Shipment.objects.count(), initial_shipment_count)
        self.assertEqual(ShipmentAddress.objects.count(), initial_address_count)
        self.assertEqual(ShipmentLifecycle.objects.count(), initial_lifecycle_count)
        self.assertEqual(ShipmentEvent.objects.count(), initial_event_count)
        log_shipment_created_mock.assert_not_called()
        dispatch_mock.assert_not_called()

    def test_create_shipment_raises_exception_when_required_address_fields_are_missing(self):
        """Raise InvalidShippingAddressException for missing required address fields."""
        customer = self.create_user()
        order = self.create_order(customer=customer)

        with self.assertRaises(InvalidShippingAddressException) as context:
            ShippingCreationService.create_shipment(
                order=order,
                customer=customer,
                shipping_method=Shipment.METHOD_STANDARD,
                address_data=self.get_address_data(city="", postal_code=""),
            )

        self.assertEqual(
            str(context.exception),
            "Missing required shipping address fields: city, postal_code.",
        )

    @patch("ech.shipping.services.shipping_creation_service.DomainEventDispatcher.dispatch")
    @patch("ech.shipping.services.shipping_creation_service.ShippingLogService.log_shipment_created")
    def test_create_shipment_does_not_create_records_when_address_is_invalid(
        self,
        log_shipment_created_mock,
        dispatch_mock,
    ):
        """Do not create shipment aggregate when address data is invalid."""
        customer = self.create_user()
        order = self.create_order(customer=customer)

        with self.assertRaises(InvalidShippingAddressException):
            ShippingCreationService.create_shipment(
                order=order,
                customer=customer,
                shipping_method=Shipment.METHOD_STANDARD,
                address_data=self.get_address_data(full_name=None),
            )

        self.assertEqual(Shipment.objects.count(), 0)
        self.assertEqual(ShipmentAddress.objects.count(), 0)
        self.assertEqual(ShipmentLifecycle.objects.count(), 0)
        self.assertEqual(ShipmentEvent.objects.count(), 0)
        log_shipment_created_mock.assert_not_called()
        dispatch_mock.assert_not_called()

    def test_validate_shipment_does_not_exist_allows_new_order(self):
        """Allow shipment creation validation when order has no shipment."""
        customer = self.create_user()
        order = self.create_order(customer=customer)

        ShippingCreationService._validate_shipment_does_not_exist(order=order)

    def test_validate_shipment_does_not_exist_raises_for_existing_shipment(self):
        """Raise ShipmentAlreadyExistsException when order already has shipment."""
        customer = self.create_user()
        order = self.create_order(customer=customer)
        self.create_existing_shipment(order=order, customer=customer)

        with self.assertRaises(ShipmentAlreadyExistsException):
            ShippingCreationService._validate_shipment_does_not_exist(order=order)

    def test_validate_address_data_accepts_complete_address(self):
        """Accept address validation when all required fields are present."""
        ShippingCreationService._validate_address_data(
            address_data=self.get_address_data()
        )

    def test_validate_address_data_raises_for_multiple_missing_fields(self):
        """Raise InvalidShippingAddressException listing all missing fields."""
        with self.assertRaises(InvalidShippingAddressException) as context:
            ShippingCreationService._validate_address_data(
                address_data=self.get_address_data(
                    full_name="",
                    address_line=None,
                    country="",
                )
            )

        self.assertEqual(
            str(context.exception),
            "Missing required shipping address fields: "
            "full_name, address_line, country.",
        )

    def create_existing_shipment(self, **kwargs):
        data = {
            "order": kwargs["order"],
            "customer": kwargs["customer"],
            "status": Shipment.STATUS_PENDING,
            "shipping_method": Shipment.METHOD_STANDARD,
            "tracking_code": f"TRACK-{uuid.uuid4().hex[:10].upper()}",
            "shipping_cost": Decimal("10.00"),
            "currency": "USD",
        }
        return Shipment.objects.create(**data)