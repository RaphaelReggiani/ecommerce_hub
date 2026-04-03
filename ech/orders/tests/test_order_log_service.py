from unittest.mock import patch
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from ech.orders.models import Order
from ech.orders.services.order_log_service import OrderLogService


User = get_user_model()


class BaseOrderLoggingFactoryMixin:

    def create_user(self):
        suffix = uuid.uuid4().hex[:8]

        return User.objects.create_user(
            email=f"user_{suffix}@test.com",
            password="StrongPassword123",
            user_name=f"User {suffix}",
            is_active=True,
            email_confirmed=True,
        )

    def create_order(self):
        customer = self.create_user()

        return Order.objects.create(
            customer=customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
            currency="USD",
        )


class OrderLogServiceTestCase(BaseOrderLoggingFactoryMixin, TestCase):

    @patch("ech.orders.services.order_log_service.logger.info")
    def test_log_order_created(self, logger_mock):
        order = self.create_order()

        OrderLogService.log_order_created(order=order)

        logger_mock.assert_called_once()

        args, kwargs = logger_mock.call_args
        self.assertEqual(args[0], "order_created")

        payload = kwargs["extra"]

        self.assertEqual(payload["event"], "order_created")
        self.assertEqual(payload["order_id"], str(order.id))
        self.assertEqual(payload["customer_id"], order.customer_id)
        self.assertEqual(payload["status"], order.status)
        self.assertEqual(payload["payment_status"], order.payment_status)
        self.assertEqual(payload["shipping_status"], order.shipping_status)

    @patch("ech.orders.services.order_log_service.logger.info")
    def test_log_idempotency_replay(self, logger_mock):
        order = self.create_order()
        key = uuid.uuid4()

        OrderLogService.log_idempotency_replay(
            order=order,
            idempotency_key=key,
        )

        logger_mock.assert_called_once()

        args, kwargs = logger_mock.call_args
        self.assertEqual(args[0], "order_idempotency_replay")

        payload = kwargs["extra"]

        self.assertEqual(payload["event"], "order_idempotency_replay")
        self.assertEqual(payload["order_id"], str(order.id))
        self.assertEqual(payload["customer_id"], order.customer_id)
        self.assertEqual(payload["idempotency_key"], str(key))

    @patch("ech.orders.services.order_log_service.logger.warning")
    def test_log_invalid_status_transition(self, logger_mock):
        order = self.create_order()
        user = self.create_user()

        OrderLogService.log_invalid_status_transition(
            order=order,
            attempted_action="ship_order",
            performed_by=user,
            reason="invalid",
        )

        logger_mock.assert_called_once()

        args, kwargs = logger_mock.call_args
        self.assertEqual(args[0], "order_invalid_status_transition")

        payload = kwargs["extra"]

        self.assertEqual(payload["event"], "order_invalid_status_transition")
        self.assertEqual(payload["order_id"], str(order.id))
        self.assertEqual(payload["customer_id"], order.customer_id)
        self.assertEqual(payload["performed_by_id"], user.id)
        self.assertEqual(payload["reason"], "invalid")
        self.assertEqual(payload["metadata"]["attempted_action"], "ship_order")

    @patch("ech.orders.services.order_log_service.logger.info")
    def test_log_order_cancelled(self, logger_mock):
        order = self.create_order()
        user = self.create_user()

        OrderLogService.log_order_cancelled(
            order=order,
            performed_by=user,
        )

        logger_mock.assert_called_once()

        args, kwargs = logger_mock.call_args
        self.assertEqual(args[0], "order_cancelled")

        payload = kwargs["extra"]

        self.assertEqual(payload["event"], "order_cancelled")
        self.assertEqual(payload["order_id"], str(order.id))
        self.assertEqual(payload["customer_id"], order.customer_id)
        self.assertEqual(payload["performed_by_id"], user.id)