from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ech.orders.models import Order
from ech.shipping.models import Shipment, ShipmentTrackingUpdate
from ech.shipping.services.shipping_log_service import ShippingLogService


User = get_user_model()


class BaseShippingLoggingFactoryMixin:
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

    def create_tracking_update(self, **kwargs):
        shipment = kwargs.pop("shipment")

        data = {
            "shipment": shipment,
            "status": Shipment.STATUS_IN_TRANSIT,
            "location": "Sao Paulo Hub",
            "description": "Package scanned at hub.",
            "raw_payload": {"carrier_status": "hub_received"},
            "event_at": timezone.now(),
        }
        data.update(kwargs)
        return ShipmentTrackingUpdate.objects.create(**data)


class ShippingLogServiceTestCase(BaseShippingLoggingFactoryMixin, TestCase):
    @patch("ech.shipping.services.shipping_log_service.logger.info")
    def test_log_shipment_created_logs_expected_payload(self, logger_info_mock):
        """Log shipment creation with expected structured payload."""
        shipment = self.create_shipment()
        performed_by = self.create_user(
            email="ops@company.com",
            user_name="Operations User",
            role=User.ROLE_OPERATIONS_STAFF,
        )

        ShippingLogService.log_shipment_created(
            shipment=shipment,
            performed_by=performed_by,
        )

        logger_info_mock.assert_called_once_with(
            "Shipment created.",
            extra={
                "shipment_id": str(shipment.id),
                "order_id": str(shipment.order_id),
                "customer_id": str(shipment.customer_id),
                "status": shipment.status,
                "shipping_method": shipment.shipping_method,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @patch("ech.shipping.services.shipping_log_service.logger.info")
    def test_log_shipment_created_logs_none_when_performed_by_is_missing(
        self,
        logger_info_mock,
    ):
        """Log shipment creation with null performer when omitted."""
        shipment = self.create_shipment()

        ShippingLogService.log_shipment_created(
            shipment=shipment,
            performed_by=None,
        )

        logger_info_mock.assert_called_once_with(
            "Shipment created.",
            extra={
                "shipment_id": str(shipment.id),
                "order_id": str(shipment.order_id),
                "customer_id": str(shipment.customer_id),
                "status": shipment.status,
                "shipping_method": shipment.shipping_method,
                "performed_by_id": None,
            },
        )

    @patch("ech.shipping.services.shipping_log_service.logger.info")
    def test_log_shipment_updated_logs_expected_payload(self, logger_info_mock):
        """Log shipment update with changed field details."""
        shipment = self.create_shipment(status=Shipment.STATUS_PREPARING)
        performed_by = self.create_user(
            email="ops2@company.com",
            user_name="Operations User 2",
            role=User.ROLE_OPERATIONS_STAFF,
        )

        ShippingLogService.log_shipment_updated(
            shipment=shipment,
            shipment_changed_fields=["carrier_name", "tracking_code"],
            address_changed_fields=["city", "postal_code"],
            performed_by=performed_by,
        )

        logger_info_mock.assert_called_once_with(
            "Shipment updated.",
            extra={
                "shipment_id": str(shipment.id),
                "order_id": str(shipment.order_id),
                "customer_id": str(shipment.customer_id),
                "status": shipment.status,
                "shipment_changed_fields": ["carrier_name", "tracking_code"],
                "address_changed_fields": ["city", "postal_code"],
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @patch("ech.shipping.services.shipping_log_service.logger.info")
    def test_log_shipment_updated_uses_empty_lists_by_default(
        self,
        logger_info_mock,
    ):
        """Log shipment update with empty changed field lists by default."""
        shipment = self.create_shipment()

        ShippingLogService.log_shipment_updated(
            shipment=shipment,
            shipment_changed_fields=None,
            address_changed_fields=None,
            performed_by=None,
        )

        logger_info_mock.assert_called_once_with(
            "Shipment updated.",
            extra={
                "shipment_id": str(shipment.id),
                "order_id": str(shipment.order_id),
                "customer_id": str(shipment.customer_id),
                "status": shipment.status,
                "shipment_changed_fields": [],
                "address_changed_fields": [],
                "performed_by_id": None,
            },
        )

    @patch("ech.shipping.services.shipping_log_service.logger.info")
    def test_log_shipment_status_changed_logs_expected_payload(
        self,
        logger_info_mock,
    ):
        """Log shipment status transition with previous and new status."""
        shipment = self.create_shipment(status=Shipment.STATUS_PREPARING)
        performed_by = self.create_user(
            email="ops3@company.com",
            user_name="Operations User 3",
            role=User.ROLE_OPERATIONS_STAFF,
        )

        ShippingLogService.log_shipment_status_changed(
            shipment=shipment,
            previous_status=Shipment.STATUS_PREPARING,
            new_status=Shipment.STATUS_SHIPPED,
            performed_by=performed_by,
        )

        logger_info_mock.assert_called_once_with(
            "Shipment status changed.",
            extra={
                "shipment_id": str(shipment.id),
                "order_id": str(shipment.order_id),
                "customer_id": str(shipment.customer_id),
                "previous_status": Shipment.STATUS_PREPARING,
                "new_status": Shipment.STATUS_SHIPPED,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @patch("ech.shipping.services.shipping_log_service.logger.info")
    def test_log_shipment_cancelled_logs_expected_payload(self, logger_info_mock):
        """Log shipment cancellation with current status."""
        shipment = self.create_shipment(status=Shipment.STATUS_CANCELLED)
        performed_by = self.create_user(
            email="ops4@company.com",
            user_name="Operations User 4",
            role=User.ROLE_OPERATIONS_STAFF,
        )

        ShippingLogService.log_shipment_cancelled(
            shipment=shipment,
            performed_by=performed_by,
        )

        logger_info_mock.assert_called_once_with(
            "Shipment cancelled.",
            extra={
                "shipment_id": str(shipment.id),
                "order_id": str(shipment.order_id),
                "customer_id": str(shipment.customer_id),
                "status": shipment.status,
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @patch("ech.shipping.services.shipping_log_service.logger.info")
    def test_log_tracking_updated_logs_expected_payload(self, logger_info_mock):
        """Log shipment tracking update with tracking event details."""
        shipment = self.create_shipment(status=Shipment.STATUS_IN_TRANSIT)
        tracking_update = self.create_tracking_update(shipment=shipment)
        performed_by = self.create_user(
            email="ops5@company.com",
            user_name="Operations User 5",
            role=User.ROLE_OPERATIONS_STAFF,
        )

        ShippingLogService.log_tracking_updated(
            shipment=shipment,
            tracking_update=tracking_update,
            performed_by=performed_by,
        )

        logger_info_mock.assert_called_once_with(
            "Shipment tracking updated.",
            extra={
                "shipment_id": str(shipment.id),
                "order_id": str(shipment.order_id),
                "customer_id": str(shipment.customer_id),
                "tracking_update_id": tracking_update.id,
                "tracking_status": tracking_update.status,
                "tracking_location": tracking_update.location,
                "tracking_event_at": tracking_update.event_at.isoformat(),
                "performed_by_id": getattr(performed_by, "id", None),
            },
        )

    @patch("ech.shipping.services.shipping_log_service.logger.info")
    def test_log_tracking_updated_logs_none_when_performed_by_is_missing(
        self,
        logger_info_mock,
    ):
        """Log tracking update with null performer when omitted."""
        shipment = self.create_shipment()
        tracking_update = self.create_tracking_update(shipment=shipment)

        ShippingLogService.log_tracking_updated(
            shipment=shipment,
            tracking_update=tracking_update,
            performed_by=None,
        )

        logger_info_mock.assert_called_once_with(
            "Shipment tracking updated.",
            extra={
                "shipment_id": str(shipment.id),
                "order_id": str(shipment.order_id),
                "customer_id": str(shipment.customer_id),
                "tracking_update_id": tracking_update.id,
                "tracking_status": tracking_update.status,
                "tracking_location": tracking_update.location,
                "tracking_event_at": tracking_update.event_at.isoformat(),
                "performed_by_id": None,
            },
        )