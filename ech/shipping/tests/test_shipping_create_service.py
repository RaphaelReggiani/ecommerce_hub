from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch
import uuid

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from ech.orders.models import Order
from ech.shipping.exceptions import (
    IdempotencyConflictException,
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

    def create_existing_shipment(self, **kwargs):
        data = {
            "order": kwargs["order"],
            "customer": kwargs["customer"],
            "status": Shipment.STATUS_PENDING,
            "shipping_method": kwargs.get(
                "shipping_method",
                Shipment.METHOD_STANDARD,
            ),
            "carrier_name": kwargs.get("carrier_name", ""),
            "tracking_code": kwargs.get(
                "tracking_code",
                f"TRACK-{uuid.uuid4().hex[:10].upper()}",
            ),
            "external_reference": kwargs.get("external_reference"),
            "idempotency_key": kwargs.get("idempotency_key"),
            "shipping_cost": kwargs.get("shipping_cost", Decimal("10.00")),
            "currency": kwargs.get("currency", "USD"),
            "estimated_delivery_date": kwargs.get("estimated_delivery_date"),
        }
        shipment = Shipment.objects.create(**data)

        ShipmentAddress.objects.create(
            shipment=shipment,
            full_name=kwargs.get("full_name", "User Tester"),
            address_line=kwargs.get("address_line", "Av. Paulista, 1000"),
            city=kwargs.get("city", "Sao Paulo"),
            state=kwargs.get("state", "SP"),
            country=kwargs.get("country", "Brazil"),
            postal_code=kwargs.get("postal_code", "01310-100"),
            phone=kwargs.get("phone", "11999999999"),
            delivery_instructions=kwargs.get(
                "delivery_instructions",
                "Leave at concierge.",
            ),
        )

        ShipmentLifecycle.objects.create(shipment=shipment)
        return shipment


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
        idempotency_key = uuid.uuid4()
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
            idempotency_key=idempotency_key,
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
        self.assertEqual(shipment.idempotency_key, idempotency_key)

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
                "idempotency_key": str(idempotency_key),
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
                "idempotency_key": None,
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

    @patch("ech.shipping.services.shipping_creation_service.DomainEventDispatcher.dispatch")
    @patch("ech.shipping.services.shipping_creation_service.ShippingLogService.log_shipment_created")
    @patch("ech.shipping.services.shipping_creation_service.ShipmentCreatedEvent")
    def test_create_shipment_reuses_existing_shipment_for_same_idempotency_and_payload(
        self,
        shipment_created_event_mock,
        log_shipment_created_mock,
        dispatch_mock,
    ):
        """Reuse existing shipment when idempotency key is replayed with same payload."""
        customer = self.create_user()
        order = self.create_order(customer=customer)
        idempotency_key = uuid.uuid4()
        estimated_delivery_date = timezone.now().date() + timedelta(days=3)
        address_data = self.get_address_data()

        first_shipment = ShippingCreationService.create_shipment(
            order=order,
            customer=customer,
            shipping_method=Shipment.METHOD_STANDARD,
            address_data=address_data,
            shipping_cost=Decimal("12.50"),
            currency="USD",
            carrier_name="DHL",
            tracking_code="TRACK-IDEMP-001",
            external_reference="EXT-IDEMP-001",
            estimated_delivery_date=estimated_delivery_date,
            idempotency_key=idempotency_key,
        )

        second_shipment = ShippingCreationService.create_shipment(
            order=order,
            customer=customer,
            shipping_method=Shipment.METHOD_STANDARD,
            address_data=address_data,
            shipping_cost=Decimal("12.50"),
            currency="USD",
            carrier_name="DHL",
            tracking_code="TRACK-IDEMP-001",
            external_reference="EXT-IDEMP-001",
            estimated_delivery_date=estimated_delivery_date,
            idempotency_key=idempotency_key,
        )

        self.assertEqual(first_shipment, second_shipment)
        self.assertEqual(Shipment.objects.count(), 1)
        self.assertEqual(ShipmentAddress.objects.count(), 1)
        self.assertEqual(ShipmentLifecycle.objects.count(), 1)
        self.assertEqual(ShipmentEvent.objects.count(), 1)

        log_shipment_created_mock.assert_called_once()
        shipment_created_event_mock.assert_called_once()
        dispatch_mock.assert_called_once()

    @patch("ech.shipping.services.shipping_creation_service.DomainEventDispatcher.dispatch")
    @patch("ech.shipping.services.shipping_creation_service.ShippingLogService.log_shipment_created")
    def test_create_shipment_raises_conflict_for_same_idempotency_with_different_payload(
        self,
        log_shipment_created_mock,
        dispatch_mock,
    ):
        """Raise IdempotencyConflictException when same key is reused with different payload."""
        customer = self.create_user()
        order = self.create_order(customer=customer)
        idempotency_key = uuid.uuid4()

        ShippingCreationService.create_shipment(
            order=order,
            customer=customer,
            shipping_method=Shipment.METHOD_STANDARD,
            address_data=self.get_address_data(city="Sao Paulo"),
            shipping_cost=Decimal("10.00"),
            currency="USD",
            carrier_name="DHL",
            tracking_code="TRACK-CONFLICT-001",
            external_reference="EXT-CONFLICT-001",
            idempotency_key=idempotency_key,
        )

        with self.assertRaises(IdempotencyConflictException):
            ShippingCreationService.create_shipment(
                order=order,
                customer=customer,
                shipping_method=Shipment.METHOD_EXPRESS,
                address_data=self.get_address_data(city="Campinas"),
                shipping_cost=Decimal("99.99"),
                currency="BRL",
                carrier_name="FedEx",
                tracking_code="TRACK-CONFLICT-999",
                external_reference="EXT-CONFLICT-999",
                idempotency_key=idempotency_key,
            )

        self.assertEqual(Shipment.objects.count(), 1)
        self.assertEqual(ShipmentAddress.objects.count(), 1)
        self.assertEqual(ShipmentLifecycle.objects.count(), 1)
        self.assertEqual(ShipmentEvent.objects.count(), 1)
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

    def test_create_shipment_returns_resolved_shipment_after_integrity_conflict(self):
        """Return resolved shipment when concurrent integrity conflict is recoverable."""
        customer = self.create_user()
        order = self.create_order(customer=customer)
        address_data = self.get_address_data()

        resolved_shipment = self.create_existing_shipment(
            order=order,
            customer=customer,
            idempotency_key=uuid.uuid4(),
        )

        with patch(
            "ech.shipping.services.shipping_creation_service."
            "ShippingCreationService._get_shipment_by_idempotency_key"
        ) as get_by_idempotency_mock, patch(
            "ech.shipping.services.shipping_creation_service.Shipment.objects.create"
        ) as shipment_create_mock, patch(
            "ech.shipping.services.shipping_creation_service."
            "ShippingCreationService._resolve_integrity_conflict"
        ) as resolve_integrity_conflict_mock, patch(
            "ech.shipping.services.shipping_creation_service."
            "ShippingCreationService._validate_shipment_does_not_exist"
        ) as validate_does_not_exist_mock:
            get_by_idempotency_mock.return_value = None
            validate_does_not_exist_mock.return_value = None
            shipment_create_mock.side_effect = IntegrityError("unique constraint")
            resolve_integrity_conflict_mock.return_value = resolved_shipment

            result = ShippingCreationService.create_shipment(
                order=order,
                customer=customer,
                shipping_method=Shipment.METHOD_STANDARD,
                address_data=address_data,
                idempotency_key=resolved_shipment.idempotency_key,
            )

        self.assertEqual(result, resolved_shipment)
        get_by_idempotency_mock.assert_called_once_with(
            idempotency_key=resolved_shipment.idempotency_key,
        )
        resolve_integrity_conflict_mock.assert_called_once()

    def test_create_shipment_reraises_integrity_error_when_conflict_cannot_be_resolved(self):
        """Re-raise IntegrityError when concurrent conflict cannot be resolved."""
        customer = self.create_user()
        order = self.create_order(customer=customer)

        with patch(
            "ech.shipping.services.shipping_creation_service."
            "ShippingCreationService._get_shipment_by_idempotency_key"
        ) as get_by_idempotency_mock, patch(
            "ech.shipping.services.shipping_creation_service.Shipment.objects.create"
        ) as shipment_create_mock, patch(
            "ech.shipping.services.shipping_creation_service."
            "ShippingCreationService._resolve_integrity_conflict"
        ) as resolve_integrity_conflict_mock, patch(
            "ech.shipping.services.shipping_creation_service."
            "ShippingCreationService._validate_shipment_does_not_exist"
        ) as validate_does_not_exist_mock:
            get_by_idempotency_mock.return_value = None
            validate_does_not_exist_mock.return_value = None
            shipment_create_mock.side_effect = IntegrityError("unique constraint")
            resolve_integrity_conflict_mock.return_value = None

            with self.assertRaises(IntegrityError):
                ShippingCreationService.create_shipment(
                    order=order,
                    customer=customer,
                    shipping_method=Shipment.METHOD_STANDARD,
                    address_data=self.get_address_data(),
                    idempotency_key=uuid.uuid4(),
                )

    def test_get_shipment_by_idempotency_key_returns_matching_shipment(self):
        """Return existing shipment when idempotency key matches."""
        customer = self.create_user()
        order = self.create_order(customer=customer)
        idempotency_key = uuid.uuid4()
        shipment = self.create_existing_shipment(
            order=order,
            customer=customer,
            idempotency_key=idempotency_key,
        )

        result = ShippingCreationService._get_shipment_by_idempotency_key(
            idempotency_key=idempotency_key,
        )

        self.assertEqual(result, shipment)

    def test_get_shipment_by_idempotency_key_returns_none_for_unknown_key(self):
        """Return none when idempotency key does not exist."""
        result = ShippingCreationService._get_shipment_by_idempotency_key(
            idempotency_key=uuid.uuid4(),
        )

        self.assertIsNone(result)

    def test_resolve_integrity_conflict_returns_existing_shipment_for_same_idempotent_request(
        self,
    ):
        """Return existing shipment when conflict matches same idempotent payload."""
        customer = self.create_user()
        order = self.create_order(customer=customer)
        idempotency_key = uuid.uuid4()
        estimated_delivery_date = timezone.now().date() + timedelta(days=4)
        address_data = self.get_address_data()

        shipment = self.create_existing_shipment(
            order=order,
            customer=customer,
            shipping_method=Shipment.METHOD_EXPRESS,
            carrier_name="DHL",
            tracking_code="TRACK-RESOLVE-001",
            external_reference="EXT-RESOLVE-001",
            idempotency_key=idempotency_key,
            shipping_cost=Decimal("15.50"),
            currency="USD",
            estimated_delivery_date=estimated_delivery_date,
            **address_data,
        )

        result = ShippingCreationService._resolve_integrity_conflict(
            order=order,
            customer=customer,
            shipping_method=Shipment.METHOD_EXPRESS,
            address_data=ShippingCreationService._normalized_address_data(
                address_data=address_data,
            ),
            shipping_cost=ShippingCreationService._normalized_decimal("15.50"),
            currency="USD",
            carrier_name="DHL",
            tracking_code="TRACK-RESOLVE-001",
            external_reference="EXT-RESOLVE-001",
            estimated_delivery_date=estimated_delivery_date,
            idempotency_key=idempotency_key,
        )

        self.assertEqual(result, shipment)

    def test_resolve_integrity_conflict_raises_conflict_for_mismatched_idempotent_payload(
        self,
    ):
        """Raise IdempotencyConflictException when existing idempotent payload differs."""
        customer = self.create_user()
        order = self.create_order(customer=customer)
        idempotency_key = uuid.uuid4()

        self.create_existing_shipment(
            order=order,
            customer=customer,
            shipping_method=Shipment.METHOD_STANDARD,
            carrier_name="DHL",
            tracking_code="TRACK-MISMATCH-001",
            external_reference="EXT-MISMATCH-001",
            idempotency_key=idempotency_key,
            shipping_cost=Decimal("10.00"),
            currency="USD",
            estimated_delivery_date=timezone.now().date() + timedelta(days=2),
            **self.get_address_data(city="Sao Paulo"),
        )

        with self.assertRaises(IdempotencyConflictException):
            ShippingCreationService._resolve_integrity_conflict(
                order=order,
                customer=customer,
                shipping_method=Shipment.METHOD_EXPRESS,
                address_data=ShippingCreationService._normalized_address_data(
                    address_data=self.get_address_data(city="Campinas"),
                ),
                shipping_cost=ShippingCreationService._normalized_decimal("50.00"),
                currency="BRL",
                carrier_name="FedEx",
                tracking_code="TRACK-MISMATCH-999",
                external_reference="EXT-MISMATCH-999",
                estimated_delivery_date=timezone.now().date() + timedelta(days=9),
                idempotency_key=idempotency_key,
            )

    def test_resolve_integrity_conflict_raises_shipment_already_exists_without_matching_idempotency(
        self,
    ):
        """Raise ShipmentAlreadyExistsException when order already has shipment and no reusable key exists."""
        customer = self.create_user()
        order = self.create_order(customer=customer)
        self.create_existing_shipment(order=order, customer=customer)

        with self.assertRaises(ShipmentAlreadyExistsException):
            ShippingCreationService._resolve_integrity_conflict(
                order=order,
                customer=customer,
                shipping_method=Shipment.METHOD_STANDARD,
                address_data=ShippingCreationService._normalized_address_data(
                    address_data=self.get_address_data(),
                ),
                shipping_cost=ShippingCreationService._normalized_decimal("10.00"),
                currency="USD",
                carrier_name="",
                tracking_code=None,
                external_reference=None,
                estimated_delivery_date=None,
                idempotency_key=uuid.uuid4(),
            )

    def test_validate_idempotent_reuse_accepts_equivalent_payload(self):
        """Accept idempotent reuse when shipment payload matches exactly."""
        customer = self.create_user()
        order = self.create_order(customer=customer)
        estimated_delivery_date = timezone.now().date() + timedelta(days=5)
        address_data = self.get_address_data()
        shipment = self.create_existing_shipment(
            order=order,
            customer=customer,
            shipping_method=Shipment.METHOD_STANDARD,
            carrier_name="DHL",
            tracking_code="TRACK-VALIDATE-001",
            external_reference="EXT-VALIDATE-001",
            shipping_cost=Decimal("10.00"),
            currency="USD",
            estimated_delivery_date=estimated_delivery_date,
            **address_data,
        )

        ShippingCreationService._validate_idempotent_reuse(
            shipment=shipment,
            order=order,
            customer=customer,
            shipping_method=Shipment.METHOD_STANDARD,
            address_data=ShippingCreationService._normalized_address_data(
                address_data=address_data,
            ),
            shipping_cost=ShippingCreationService._normalized_decimal("10.00"),
            currency="USD",
            carrier_name="DHL",
            tracking_code="TRACK-VALIDATE-001",
            external_reference="EXT-VALIDATE-001",
            estimated_delivery_date=estimated_delivery_date,
        )

    def test_validate_idempotent_reuse_raises_for_different_payload(self):
        """Raise IdempotencyConflictException when idempotent reuse payload differs."""
        customer = self.create_user()
        order = self.create_order(customer=customer)
        shipment = self.create_existing_shipment(
            order=order,
            customer=customer,
            shipping_method=Shipment.METHOD_STANDARD,
            carrier_name="DHL",
            tracking_code="TRACK-DIFF-001",
            shipping_cost=Decimal("10.00"),
            currency="USD",
            **self.get_address_data(),
        )

        with self.assertRaises(IdempotencyConflictException):
            ShippingCreationService._validate_idempotent_reuse(
                shipment=shipment,
                order=order,
                customer=customer,
                shipping_method=Shipment.METHOD_EXPRESS,
                address_data=ShippingCreationService._normalized_address_data(
                    address_data=self.get_address_data(city="Campinas"),
                ),
                shipping_cost=ShippingCreationService._normalized_decimal("99.99"),
                currency="BRL",
                carrier_name="FedEx",
                tracking_code="TRACK-DIFF-999",
                external_reference="EXT-DIFF-999",
                estimated_delivery_date=timezone.now().date() + timedelta(days=10),
            )

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

    def test_normalized_address_data_fills_optional_blank_values(self):
        """Normalize optional address fields to blank strings."""
        normalized = ShippingCreationService._normalized_address_data(
            address_data=self.get_address_data(
                phone=None,
                delivery_instructions=None,
            )
        )

        self.assertEqual(normalized["phone"], "")
        self.assertEqual(normalized["delivery_instructions"], "")

    def test_normalized_decimal_returns_decimal_instance(self):
        """Normalize decimal-like values into Decimal for safe comparison."""
        normalized = ShippingCreationService._normalized_decimal("10.50")

        self.assertEqual(normalized, Decimal("10.50"))

    def test_lock_order_returns_same_persisted_order(self):
        """Lock and return the same order instance from the database."""
        customer = self.create_user()
        order = self.create_order(customer=customer)

        locked_order = ShippingCreationService._lock_order(order=order)

        self.assertEqual(locked_order.pk, order.pk)