from unittest.mock import patch
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from ech.orders.models import Order
from ech.shipping.constants.messages import (
    SHIPMENT_CANCELLATION_NOT_ALLOWED,
)
from ech.shipping.exceptions import (
    ShipmentAlreadyCancelledException,
    ShipmentAlreadyDeliveredException,
    ShipmentCancellationNotAllowedException,
)
from ech.shipping.models import Shipment
from ech.shipping.services.shipping_cancellation_service import (
    ShippingCancellationService,
)


User = get_user_model()


class BaseShippingCancellationFactoryMixin:
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
        return Shipment.objects.create(**data)


class ShippingCancellationServiceTestCase(
    BaseShippingCancellationFactoryMixin,
    TestCase,
):
    @patch(
        "ech.shipping.services.shipping_cancellation_service."
        "ShippingLogService.log_shipment_cancelled"
    )
    @patch(
        "ech.shipping.services.shipping_cancellation_service."
        "ShippingStatusService.update_status"
    )
    def test_cancel_shipment_success(
        self,
        update_status_mock,
        log_shipment_cancelled_mock,
    ):
        """Cancel a shipment successfully when business rules allow it."""
        shipment = self.create_shipment(status=Shipment.STATUS_PENDING)
        performed_by = self.create_user(
            email="ops@company.com",
            user_name="Operations User",
            role=User.ROLE_OPERATIONS_STAFF,
        )

        update_status_mock.return_value = shipment

        result = ShippingCancellationService.cancel_shipment(
            shipment=shipment,
            performed_by=performed_by,
            metadata={"source": "unit-test"},
        )

        self.assertEqual(result, shipment)

        update_status_mock.assert_called_once_with(
            shipment=shipment,
            new_status=Shipment.STATUS_CANCELLED,
            performed_by=performed_by,
            metadata={
                "action": "shipment_cancelled",
                "source": "unit-test",
            },
        )

        log_shipment_cancelled_mock.assert_called_once_with(
            shipment=shipment,
            performed_by=performed_by,
        )

    @patch(
        "ech.shipping.services.shipping_cancellation_service."
        "ShippingLogService.log_shipment_cancelled"
    )
    @patch(
        "ech.shipping.services.shipping_cancellation_service."
        "ShippingStatusService.update_status"
    )
    def test_cancel_shipment_success_without_metadata(
        self,
        update_status_mock,
        log_shipment_cancelled_mock,
    ):
        """Cancel a shipment successfully with default cancellation metadata."""
        shipment = self.create_shipment(status=Shipment.STATUS_PREPARING)
        update_status_mock.return_value = shipment

        result = ShippingCancellationService.cancel_shipment(
            shipment=shipment,
        )

        self.assertEqual(result, shipment)

        update_status_mock.assert_called_once_with(
            shipment=shipment,
            new_status=Shipment.STATUS_CANCELLED,
            performed_by=None,
            metadata={"action": "shipment_cancelled"},
        )

        log_shipment_cancelled_mock.assert_called_once_with(
            shipment=shipment,
            performed_by=None,
        )

    @patch(
        "ech.shipping.services.shipping_cancellation_service."
        "ShippingLogService.log_shipment_cancelled"
    )
    @patch(
        "ech.shipping.services.shipping_cancellation_service."
        "ShippingStatusService.update_status"
    )
    def test_cancel_shipment_does_not_call_side_effects_when_already_cancelled(
        self,
        update_status_mock,
        log_shipment_cancelled_mock,
    ):
        """Do not execute side effects when shipment is already cancelled."""
        shipment = self.create_shipment(status=Shipment.STATUS_CANCELLED)

        with self.assertRaises(ShipmentAlreadyCancelledException):
            ShippingCancellationService.cancel_shipment(shipment=shipment)

        update_status_mock.assert_not_called()
        log_shipment_cancelled_mock.assert_not_called()

    @patch(
        "ech.shipping.services.shipping_cancellation_service."
        "ShippingLogService.log_shipment_cancelled"
    )
    @patch(
        "ech.shipping.services.shipping_cancellation_service."
        "ShippingStatusService.update_status"
    )
    def test_cancel_shipment_does_not_call_side_effects_when_already_delivered(
        self,
        update_status_mock,
        log_shipment_cancelled_mock,
    ):
        """Do not execute side effects when shipment is already delivered."""
        shipment = self.create_shipment(status=Shipment.STATUS_DELIVERED)

        with self.assertRaises(ShipmentAlreadyDeliveredException):
            ShippingCancellationService.cancel_shipment(shipment=shipment)

        update_status_mock.assert_not_called()
        log_shipment_cancelled_mock.assert_not_called()

    @patch(
        "ech.shipping.services.shipping_cancellation_service."
        "ShippingLogService.log_shipment_cancelled"
    )
    @patch(
        "ech.shipping.services.shipping_cancellation_service."
        "ShippingStatusService.update_status"
    )
    def test_cancel_shipment_raises_for_non_cancellable_status(
        self,
        update_status_mock,
        log_shipment_cancelled_mock,
    ):
        """Raise ShipmentCancellationNotAllowedException for returned shipment."""
        shipment = self.create_shipment(status=Shipment.STATUS_RETURNED)

        with self.assertRaises(ShipmentCancellationNotAllowedException) as context:
            ShippingCancellationService.cancel_shipment(shipment=shipment)

        self.assertEqual(
            str(context.exception),
            SHIPMENT_CANCELLATION_NOT_ALLOWED,
        )
        update_status_mock.assert_not_called()
        log_shipment_cancelled_mock.assert_not_called()

    def test_validate_can_be_cancelled_allows_pending_status(self):
        """Allow cancellation validation for cancellable shipment status."""
        shipment = self.create_shipment(status=Shipment.STATUS_PENDING)

        ShippingCancellationService._validate_can_be_cancelled(
            shipment=shipment,
        )

    def test_validate_can_be_cancelled_allows_preparing_status(self):
        """Allow cancellation validation for preparing shipment status."""
        shipment = self.create_shipment(status=Shipment.STATUS_PREPARING)

        ShippingCancellationService._validate_can_be_cancelled(
            shipment=shipment,
        )

    def test_validate_can_be_cancelled_raises_for_cancelled_status(self):
        """Raise ShipmentAlreadyCancelledException for cancelled shipment."""
        shipment = self.create_shipment(status=Shipment.STATUS_CANCELLED)

        with self.assertRaises(ShipmentAlreadyCancelledException):
            ShippingCancellationService._validate_can_be_cancelled(
                shipment=shipment,
            )

    def test_validate_can_be_cancelled_raises_for_delivered_status(self):
        """Raise ShipmentAlreadyDeliveredException for delivered shipment."""
        shipment = self.create_shipment(status=Shipment.STATUS_DELIVERED)

        with self.assertRaises(ShipmentAlreadyDeliveredException):
            ShippingCancellationService._validate_can_be_cancelled(
                shipment=shipment,
            )

    def test_validate_can_be_cancelled_raises_for_non_cancellable_status(self):
        """Raise ShipmentCancellationNotAllowedException for returned shipment."""
        shipment = self.create_shipment(status=Shipment.STATUS_RETURNED)

        with self.assertRaises(ShipmentCancellationNotAllowedException) as context:
            ShippingCancellationService._validate_can_be_cancelled(
                shipment=shipment,
            )

        self.assertEqual(
            str(context.exception),
            SHIPMENT_CANCELLATION_NOT_ALLOWED,
        )

    def test_non_cancellable_statuses_contains_expected_terminal_statuses(self):
        """Expose expected non-cancellable shipment statuses."""
        self.assertEqual(
            ShippingCancellationService.NON_CANCELLABLE_STATUSES,
            {
                Shipment.STATUS_DELIVERED,
                Shipment.STATUS_RETURNED,
            },
        )