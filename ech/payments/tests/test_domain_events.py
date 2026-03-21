import uuid
from unittest.mock import patch

from django.test import SimpleTestCase

from ech.payments.domain_events.dispatcher import (
    PaymentDomainEventDispatcher,
    payment_event_dispatcher,
)
from ech.payments.domain_events.events import (
    BasePaymentDomainEvent,
    PaymentAuthorizedEvent,
    PaymentCancelledEvent,
    PaymentCapturedEvent,
    PaymentCreatedEvent,
    PaymentFailedEvent,
    PaymentProcessingStartedEvent,
    PaymentRefundCancelledEvent,
    PaymentRefundFailedEvent,
    PaymentRefundProcessedEvent,
    PaymentRefundRequestedEvent,
)
from ech.payments.domain_events.handlers import (
    handle_payment_authorized,
    handle_payment_cancelled,
    handle_payment_captured,
    handle_payment_created,
    handle_payment_failed,
    handle_payment_processing_started,
    handle_payment_refund_cancelled,
    handle_payment_refund_failed,
    handle_payment_refund_processed,
    handle_payment_refund_requested,
)
from ech.payments.domain_events.registry import register_payment_event_handlers


class PaymentDomainEventsTestCase(SimpleTestCase):
    def setUp(self):
        payment_event_dispatcher.clear()
        self.payment_id = uuid.uuid4()
        self.order_id = uuid.uuid4()
        self.customer_id = uuid.uuid4()
        self.transaction_id = uuid.uuid4()
        self.refund_id = uuid.uuid4()

    def tearDown(self):
        payment_event_dispatcher.clear()

    def test_base_payment_domain_event_sets_defaults(self):
        """Ensure base payment domain event sets default timestamp and metadata."""
        event = BasePaymentDomainEvent(payment_id=self.payment_id)

        self.assertEqual(event.payment_id, self.payment_id)
        self.assertIsNotNone(event.occurred_at)
        self.assertEqual(event.metadata, {})

    def test_payment_created_event_stores_expected_fields(self):
        """Ensure payment created event stores provided payload fields."""
        event = PaymentCreatedEvent(
            payment_id=self.payment_id,
            order_id=self.order_id,
            customer_id=self.customer_id,
            payment_reference="PAY-001",
            method="pix",
            status="pending",
            amount="100.00",
            currency="USD",
            metadata={"source": "test"},
        )

        self.assertEqual(event.payment_id, self.payment_id)
        self.assertEqual(event.order_id, self.order_id)
        self.assertEqual(event.customer_id, self.customer_id)
        self.assertEqual(event.payment_reference, "PAY-001")
        self.assertEqual(event.method, "pix")
        self.assertEqual(event.status, "pending")
        self.assertEqual(event.amount, "100.00")
        self.assertEqual(event.currency, "USD")
        self.assertEqual(event.metadata, {"source": "test"})

    def test_payment_processing_started_event_stores_statuses(self):
        """Ensure processing started event stores previous and new statuses."""
        event = PaymentProcessingStartedEvent(
            payment_id=self.payment_id,
            previous_status="pending",
            new_status="processing",
        )

        self.assertEqual(event.previous_status, "pending")
        self.assertEqual(event.new_status, "processing")

    def test_payment_authorized_event_stores_transaction_id(self):
        """Ensure authorized event stores transaction id."""
        event = PaymentAuthorizedEvent(
            payment_id=self.payment_id,
            previous_status="processing",
            new_status="authorized",
            transaction_id=self.transaction_id,
        )

        self.assertEqual(event.transaction_id, self.transaction_id)

    def test_payment_captured_event_stores_transaction_id(self):
        """Ensure captured event stores transaction id."""
        event = PaymentCapturedEvent(
            payment_id=self.payment_id,
            previous_status="authorized",
            new_status="captured",
            transaction_id=self.transaction_id,
        )

        self.assertEqual(event.transaction_id, self.transaction_id)

    def test_payment_failed_event_stores_failure_data(self):
        """Ensure failed event stores failure details."""
        event = PaymentFailedEvent(
            payment_id=self.payment_id,
            previous_status="processing",
            new_status="failed",
            transaction_id=self.transaction_id,
            failure_code="DECLINED",
            failure_message="Card declined",
        )

        self.assertEqual(event.transaction_id, self.transaction_id)
        self.assertEqual(event.failure_code, "DECLINED")
        self.assertEqual(event.failure_message, "Card declined")

    def test_payment_cancelled_event_stores_transaction_id(self):
        """Ensure cancelled event stores transaction id."""
        event = PaymentCancelledEvent(
            payment_id=self.payment_id,
            previous_status="pending",
            new_status="cancelled",
            transaction_id=self.transaction_id,
        )

        self.assertEqual(event.transaction_id, self.transaction_id)

    def test_payment_refund_requested_event_stores_refund_data(self):
        """Ensure refund requested event stores refund details."""
        event = PaymentRefundRequestedEvent(
            payment_id=self.payment_id,
            refund_id=self.refund_id,
            amount="20.00",
            reason="Customer request",
        )

        self.assertEqual(event.refund_id, self.refund_id)
        self.assertEqual(event.amount, "20.00")
        self.assertEqual(event.reason, "Customer request")

    def test_payment_refund_processed_event_stores_refund_processing_data(self):
        """Ensure refund processed event stores processing details."""
        event = PaymentRefundProcessedEvent(
            payment_id=self.payment_id,
            refund_id=self.refund_id,
            transaction_id=self.transaction_id,
            amount="20.00",
            refunded_amount="20.00",
            full_refund=False,
            partial_refund=True,
        )

        self.assertEqual(event.refund_id, self.refund_id)
        self.assertEqual(event.transaction_id, self.transaction_id)
        self.assertEqual(event.amount, "20.00")
        self.assertEqual(event.refunded_amount, "20.00")
        self.assertFalse(event.full_refund)
        self.assertTrue(event.partial_refund)

    def test_payment_refund_failed_event_stores_failure_data(self):
        """Ensure refund failed event stores refund failure payload."""
        event = PaymentRefundFailedEvent(
            payment_id=self.payment_id,
            refund_id=self.refund_id,
            amount="20.00",
            reason="Gateway error",
        )

        self.assertEqual(event.refund_id, self.refund_id)
        self.assertEqual(event.amount, "20.00")
        self.assertEqual(event.reason, "Gateway error")

    def test_payment_refund_cancelled_event_stores_cancel_data(self):
        """Ensure refund cancelled event stores cancellation payload."""
        event = PaymentRefundCancelledEvent(
            payment_id=self.payment_id,
            refund_id=self.refund_id,
            amount="20.00",
            reason="Cancelled by staff",
        )

        self.assertEqual(event.refund_id, self.refund_id)
        self.assertEqual(event.amount, "20.00")
        self.assertEqual(event.reason, "Cancelled by staff")

    def test_dispatcher_registers_handler(self):
        """Ensure dispatcher registers handler for event type."""
        dispatcher = PaymentDomainEventDispatcher()

        def handler(event):
            return event

        dispatcher.register(PaymentCreatedEvent, handler)

        handlers = dispatcher.get_handlers(PaymentCreatedEvent)
        self.assertEqual(handlers, [handler])

    def test_dispatcher_does_not_register_duplicate_handler(self):
        """Ensure dispatcher does not duplicate the same handler."""
        dispatcher = PaymentDomainEventDispatcher()

        def handler(event):
            return event

        dispatcher.register(PaymentCreatedEvent, handler)
        dispatcher.register(PaymentCreatedEvent, handler)

        handlers = dispatcher.get_handlers(PaymentCreatedEvent)
        self.assertEqual(len(handlers), 1)

    def test_dispatcher_dispatches_event_to_registered_handler(self):
        """Ensure dispatcher dispatches event to matching registered handler."""
        dispatcher = PaymentDomainEventDispatcher()
        received = []

        def handler(event):
            received.append(event)

        dispatcher.register(PaymentCreatedEvent, handler)

        event = PaymentCreatedEvent(payment_id=self.payment_id)
        dispatcher.dispatch(event)

        self.assertEqual(received, [event])

    def test_dispatcher_dispatches_to_multiple_handlers(self):
        """Ensure dispatcher dispatches event to all registered handlers."""
        dispatcher = PaymentDomainEventDispatcher()
        received = []

        def handler_one(event):
            received.append(("one", event))

        def handler_two(event):
            received.append(("two", event))

        dispatcher.register(PaymentCreatedEvent, handler_one)
        dispatcher.register(PaymentCreatedEvent, handler_two)

        event = PaymentCreatedEvent(payment_id=self.payment_id)
        dispatcher.dispatch(event)

        self.assertEqual(received, [("one", event), ("two", event)])

    def test_dispatcher_does_not_dispatch_to_other_event_type_handlers(self):
        """Ensure dispatcher uses exact event type matching."""
        dispatcher = PaymentDomainEventDispatcher()
        received = []

        def created_handler(event):
            received.append(event)

        dispatcher.register(PaymentCreatedEvent, created_handler)

        event = PaymentCancelledEvent(payment_id=self.payment_id)
        dispatcher.dispatch(event)

        self.assertEqual(received, [])

    def test_dispatcher_clear_removes_all_handlers(self):
        """Ensure dispatcher clear removes registered handlers."""
        dispatcher = PaymentDomainEventDispatcher()

        def handler(event):
            return event

        dispatcher.register(PaymentCreatedEvent, handler)
        dispatcher.clear()

        self.assertEqual(dispatcher.get_handlers(PaymentCreatedEvent), [])

    @patch("ech.payments.domain_events.handlers.logger.info")
    def test_handle_payment_created_logs_event(self, mock_info):
        """Ensure created handler logs expected info payload."""
        event = PaymentCreatedEvent(
            payment_id=self.payment_id,
            order_id=self.order_id,
            customer_id=self.customer_id,
            payment_reference="PAY-001",
            method="pix",
            status="pending",
            amount="100.00",
            currency="USD",
            metadata={"source": "test"},
        )

        handle_payment_created(event)

        mock_info.assert_called_once()

    @patch("ech.payments.domain_events.handlers.logger.info")
    def test_handle_payment_processing_started_logs_event(self, mock_info):
        """Ensure processing started handler logs expected info payload."""
        event = PaymentProcessingStartedEvent(
            payment_id=self.payment_id,
            previous_status="pending",
            new_status="processing",
            metadata={"source": "test"},
        )

        handle_payment_processing_started(event)

        mock_info.assert_called_once()

    @patch("ech.payments.domain_events.handlers.logger.info")
    def test_handle_payment_authorized_logs_event(self, mock_info):
        """Ensure authorized handler logs expected info payload."""
        event = PaymentAuthorizedEvent(
            payment_id=self.payment_id,
            previous_status="processing",
            new_status="authorized",
            transaction_id=self.transaction_id,
            metadata={"source": "test"},
        )

        handle_payment_authorized(event)

        mock_info.assert_called_once()

    @patch("ech.payments.domain_events.handlers.logger.info")
    def test_handle_payment_captured_logs_event(self, mock_info):
        """Ensure captured handler logs expected info payload."""
        event = PaymentCapturedEvent(
            payment_id=self.payment_id,
            previous_status="authorized",
            new_status="captured",
            transaction_id=self.transaction_id,
            metadata={"source": "test"},
        )

        handle_payment_captured(event)

        mock_info.assert_called_once()

    @patch("ech.payments.domain_events.handlers.logger.warning")
    def test_handle_payment_failed_logs_warning(self, mock_warning):
        """Ensure failed handler logs expected warning payload."""
        event = PaymentFailedEvent(
            payment_id=self.payment_id,
            previous_status="processing",
            new_status="failed",
            transaction_id=self.transaction_id,
            failure_code="DECLINED",
            failure_message="Card declined",
            metadata={"source": "test"},
        )

        handle_payment_failed(event)

        mock_warning.assert_called_once()

    @patch("ech.payments.domain_events.handlers.logger.info")
    def test_handle_payment_cancelled_logs_event(self, mock_info):
        """Ensure cancelled handler logs expected info payload."""
        event = PaymentCancelledEvent(
            payment_id=self.payment_id,
            previous_status="pending",
            new_status="cancelled",
            transaction_id=self.transaction_id,
            metadata={"source": "test"},
        )

        handle_payment_cancelled(event)

        mock_info.assert_called_once()

    @patch("ech.payments.domain_events.handlers.logger.info")
    def test_handle_payment_refund_requested_logs_event(self, mock_info):
        """Ensure refund requested handler logs expected info payload."""
        event = PaymentRefundRequestedEvent(
            payment_id=self.payment_id,
            refund_id=self.refund_id,
            amount="20.00",
            reason="Customer request",
            metadata={"source": "test"},
        )

        handle_payment_refund_requested(event)

        mock_info.assert_called_once()

    @patch("ech.payments.domain_events.handlers.logger.info")
    def test_handle_payment_refund_processed_logs_event(self, mock_info):
        """Ensure refund processed handler logs expected info payload."""
        event = PaymentRefundProcessedEvent(
            payment_id=self.payment_id,
            refund_id=self.refund_id,
            transaction_id=self.transaction_id,
            amount="20.00",
            refunded_amount="20.00",
            full_refund=False,
            partial_refund=True,
            metadata={"source": "test"},
        )

        handle_payment_refund_processed(event)

        mock_info.assert_called_once()

    @patch("ech.payments.domain_events.handlers.logger.warning")
    def test_handle_payment_refund_failed_logs_warning(self, mock_warning):
        """Ensure refund failed handler logs expected warning payload."""
        event = PaymentRefundFailedEvent(
            payment_id=self.payment_id,
            refund_id=self.refund_id,
            amount="20.00",
            reason="Gateway error",
            metadata={"source": "test"},
        )

        handle_payment_refund_failed(event)

        mock_warning.assert_called_once()

    @patch("ech.payments.domain_events.handlers.logger.info")
    def test_handle_payment_refund_cancelled_logs_event(self, mock_info):
        """Ensure refund cancelled handler logs expected info payload."""
        event = PaymentRefundCancelledEvent(
            payment_id=self.payment_id,
            refund_id=self.refund_id,
            amount="20.00",
            reason="Cancelled by staff",
            metadata={"source": "test"},
        )

        handle_payment_refund_cancelled(event)

        mock_info.assert_called_once()

    def test_register_payment_event_handlers_registers_all_expected_handlers(self):
        """Ensure registry registers one handler for each payment event type."""
        register_payment_event_handlers()

        self.assertEqual(
            payment_event_dispatcher.get_handlers(PaymentCreatedEvent),
            [handle_payment_created],
        )
        self.assertEqual(
            payment_event_dispatcher.get_handlers(PaymentProcessingStartedEvent),
            [handle_payment_processing_started],
        )
        self.assertEqual(
            payment_event_dispatcher.get_handlers(PaymentAuthorizedEvent),
            [handle_payment_authorized],
        )
        self.assertEqual(
            payment_event_dispatcher.get_handlers(PaymentCapturedEvent),
            [handle_payment_captured],
        )
        self.assertEqual(
            payment_event_dispatcher.get_handlers(PaymentFailedEvent),
            [handle_payment_failed],
        )
        self.assertEqual(
            payment_event_dispatcher.get_handlers(PaymentCancelledEvent),
            [handle_payment_cancelled],
        )
        self.assertEqual(
            payment_event_dispatcher.get_handlers(PaymentRefundRequestedEvent),
            [handle_payment_refund_requested],
        )
        self.assertEqual(
            payment_event_dispatcher.get_handlers(PaymentRefundProcessedEvent),
            [handle_payment_refund_processed],
        )
        self.assertEqual(
            payment_event_dispatcher.get_handlers(PaymentRefundFailedEvent),
            [handle_payment_refund_failed],
        )
        self.assertEqual(
            payment_event_dispatcher.get_handlers(PaymentRefundCancelledEvent),
            [handle_payment_refund_cancelled],
        )

    def test_register_payment_event_handlers_is_idempotent(self):
        """Ensure registry does not duplicate handlers when called twice."""
        register_payment_event_handlers()
        register_payment_event_handlers()

        self.assertEqual(
            len(payment_event_dispatcher.get_handlers(PaymentCreatedEvent)),
            1,
        )
        self.assertEqual(
            len(payment_event_dispatcher.get_handlers(PaymentRefundProcessedEvent)),
            1,
        )

    @patch("ech.payments.domain_events.handlers.logger.info")
    def test_registered_handler_dispatch_flow_executes_created_handler(self, mock_info):
        """Ensure registered created event handler is executed through dispatcher."""
        register_payment_event_handlers()

        event = PaymentCreatedEvent(
            payment_id=self.payment_id,
            order_id=self.order_id,
            customer_id=self.customer_id,
            payment_reference="PAY-001",
            method="pix",
            status="pending",
            amount="100.00",
            currency="USD",
            metadata={"source": "test"},
        )

        payment_event_dispatcher.dispatch(event)

        mock_info.assert_called_once()