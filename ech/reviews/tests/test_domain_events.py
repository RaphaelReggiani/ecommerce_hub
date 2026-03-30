import uuid
from unittest.mock import patch

from django.test import TestCase

from ech.reviews.domain_events.dispatcher import ReviewEventDispatcher
from ech.reviews.domain_events.events import (
    BaseReviewDomainEvent,
    ReviewApprovedEvent,
    ReviewCancelledEvent,
    ReviewCreatedEvent,
    ReviewHiddenEvent,
    ReviewRejectedEvent,
    ReviewRestoredEvent,
    ReviewUpdatedEvent,
)
from ech.reviews.domain_events.handlers import (
    handle_review_approved,
    handle_review_cancelled,
    handle_review_created,
    handle_review_hidden,
    handle_review_rejected,
    handle_review_restored,
    handle_review_updated,
)
from ech.reviews.domain_events.registry import register_review_event_handlers


class ReviewDomainEventsTestCase(TestCase):
    def setUp(self):
        ReviewEventDispatcher.clear()

    def tearDown(self):
        ReviewEventDispatcher.clear()

    def test_base_review_domain_event_creation(self):
        """Create base domain event with review id and metadata."""
        review_id = uuid.uuid4()

        event = BaseReviewDomainEvent(
            review_id=review_id,
            metadata={"source": "unit-test"},
        )

        self.assertEqual(event.review_id, review_id)
        self.assertEqual(event.metadata, {"source": "unit-test"})
        self.assertIsNotNone(event.occurred_at)

    def test_base_review_domain_event_metadata_defaults_to_empty_dict(self):
        """Use empty dict as default metadata."""
        event = BaseReviewDomainEvent(review_id=uuid.uuid4())

        self.assertEqual(event.metadata, {})

    def test_dispatch_calls_registered_handler(self):
        """Dispatch event to registered handler."""
        captured = []

        def handler(event):
            captured.append(event.review_id)

        ReviewEventDispatcher.register(ReviewCreatedEvent, handler)

        event = ReviewCreatedEvent(review_id=uuid.uuid4())
        ReviewEventDispatcher.dispatch(event)

        self.assertEqual(captured, [event.review_id])

    def test_dispatch_calls_multiple_handlers(self):
        """Dispatch event to multiple handlers."""
        captured = []

        def first_handler(event):
            captured.append(("first", event.review_id))

        def second_handler(event):
            captured.append(("second", event.review_id))

        ReviewEventDispatcher.register(ReviewCreatedEvent, first_handler)
        ReviewEventDispatcher.register(ReviewCreatedEvent, second_handler)

        event = ReviewCreatedEvent(review_id=uuid.uuid4())
        ReviewEventDispatcher.dispatch(event)

        self.assertEqual(len(captured), 2)
        self.assertEqual(captured[0][0], "first")
        self.assertEqual(captured[1][0], "second")

    def test_register_prevents_duplicate_handler_registration(self):
        """Prevent duplicate handler registration for same event."""
        def handler(event):
            return event

        ReviewEventDispatcher.register(ReviewCreatedEvent, handler)
        ReviewEventDispatcher.register(ReviewCreatedEvent, handler)

        handlers = ReviewEventDispatcher._handlers[ReviewCreatedEvent]

        self.assertEqual(len(handlers), 1)

    def test_dispatch_without_registered_handlers_is_safe(self):
        """Allow dispatch when no handlers are registered."""
        event = ReviewCreatedEvent(review_id=uuid.uuid4())

        ReviewEventDispatcher.dispatch(event)

        self.assertEqual(ReviewEventDispatcher._handlers, {})

    def test_clear_removes_registered_handlers(self):
        """Clear all registered handlers."""
        def handler(event):
            return event

        ReviewEventDispatcher.register(ReviewCreatedEvent, handler)
        self.assertTrue(ReviewEventDispatcher._handlers)

        ReviewEventDispatcher.clear()

        self.assertEqual(ReviewEventDispatcher._handlers, {})

    def test_registry_registers_all_review_event_handlers(self):
        """Register all handlers defined in registry."""
        register_review_event_handlers()

        self.assertIn(ReviewCreatedEvent, ReviewEventDispatcher._handlers)
        self.assertIn(ReviewUpdatedEvent, ReviewEventDispatcher._handlers)
        self.assertIn(ReviewApprovedEvent, ReviewEventDispatcher._handlers)
        self.assertIn(ReviewRejectedEvent, ReviewEventDispatcher._handlers)
        self.assertIn(ReviewHiddenEvent, ReviewEventDispatcher._handlers)
        self.assertIn(ReviewRestoredEvent, ReviewEventDispatcher._handlers)
        self.assertIn(ReviewCancelledEvent, ReviewEventDispatcher._handlers)

    def test_registry_is_idempotent(self):
        """Registering handlers multiple times must not duplicate them."""
        register_review_event_handlers()
        register_review_event_handlers()

        self.assertEqual(
            len(ReviewEventDispatcher._handlers[ReviewCreatedEvent]),
            1,
        )
        self.assertEqual(
            len(ReviewEventDispatcher._handlers[ReviewUpdatedEvent]),
            1,
        )
        self.assertEqual(
            len(ReviewEventDispatcher._handlers[ReviewApprovedEvent]),
            1,
        )
        self.assertEqual(
            len(ReviewEventDispatcher._handlers[ReviewRejectedEvent]),
            1,
        )
        self.assertEqual(
            len(ReviewEventDispatcher._handlers[ReviewHiddenEvent]),
            1,
        )
        self.assertEqual(
            len(ReviewEventDispatcher._handlers[ReviewRestoredEvent]),
            1,
        )
        self.assertEqual(
            len(ReviewEventDispatcher._handlers[ReviewCancelledEvent]),
            1,
        )

    @patch("ech.reviews.domain_events.handlers.logger.info")
    def test_handle_review_created_logs_structured_payload(self, logger_mock):
        """Log structured payload for created review event."""
        event = ReviewCreatedEvent(
            review_id=uuid.uuid4(),
            metadata={"rating": 5},
        )

        handle_review_created(event)

        logger_mock.assert_called_once()
        call_args = logger_mock.call_args
        self.assertEqual(call_args[0][0], "review_domain_event_created")
        self.assertEqual(
            call_args[1]["extra"]["payload"]["event_type"],
            "review_created",
        )

    @patch("ech.reviews.domain_events.handlers.logger.info")
    def test_handle_review_updated_logs_structured_payload(self, logger_mock):
        """Log structured payload for updated review event."""
        event = ReviewUpdatedEvent(
            review_id=uuid.uuid4(),
            metadata={"updated_fields": ["title"]},
        )

        handle_review_updated(event)

        logger_mock.assert_called_once()
        call_args = logger_mock.call_args
        self.assertEqual(call_args[0][0], "review_domain_event_updated")
        self.assertEqual(
            call_args[1]["extra"]["payload"]["event_type"],
            "review_updated",
        )

    @patch("ech.reviews.domain_events.handlers.logger.info")
    def test_handle_review_approved_logs_structured_payload(self, logger_mock):
        """Log structured payload for approved review event."""
        event = ReviewApprovedEvent(review_id=uuid.uuid4())

        handle_review_approved(event)

        logger_mock.assert_called_once()
        call_args = logger_mock.call_args
        self.assertEqual(call_args[0][0], "review_domain_event_approved")
        self.assertEqual(
            call_args[1]["extra"]["payload"]["event_type"],
            "review_approved",
        )

    @patch("ech.reviews.domain_events.handlers.logger.info")
    def test_handle_review_rejected_logs_structured_payload(self, logger_mock):
        """Log structured payload for rejected review event."""
        event = ReviewRejectedEvent(review_id=uuid.uuid4())

        handle_review_rejected(event)

        logger_mock.assert_called_once()
        call_args = logger_mock.call_args
        self.assertEqual(call_args[0][0], "review_domain_event_rejected")
        self.assertEqual(
            call_args[1]["extra"]["payload"]["event_type"],
            "review_rejected",
        )

    @patch("ech.reviews.domain_events.handlers.logger.info")
    def test_handle_review_hidden_logs_structured_payload(self, logger_mock):
        """Log structured payload for hidden review event."""
        event = ReviewHiddenEvent(review_id=uuid.uuid4())

        handle_review_hidden(event)

        logger_mock.assert_called_once()
        call_args = logger_mock.call_args
        self.assertEqual(call_args[0][0], "review_domain_event_hidden")
        self.assertEqual(
            call_args[1]["extra"]["payload"]["event_type"],
            "review_hidden",
        )

    @patch("ech.reviews.domain_events.handlers.logger.info")
    def test_handle_review_restored_logs_structured_payload(self, logger_mock):
        """Log structured payload for restored review event."""
        event = ReviewRestoredEvent(review_id=uuid.uuid4())

        handle_review_restored(event)

        logger_mock.assert_called_once()
        call_args = logger_mock.call_args
        self.assertEqual(call_args[0][0], "review_domain_event_restored")
        self.assertEqual(
            call_args[1]["extra"]["payload"]["event_type"],
            "review_restored",
        )

    @patch("ech.reviews.domain_events.handlers.logger.info")
    def test_handle_review_cancelled_logs_structured_payload(self, logger_mock):
        """Log structured payload for cancelled review event."""
        event = ReviewCancelledEvent(review_id=uuid.uuid4())

        handle_review_cancelled(event)

        logger_mock.assert_called_once()
        call_args = logger_mock.call_args
        self.assertEqual(call_args[0][0], "review_domain_event_cancelled")
        self.assertEqual(
            call_args[1]["extra"]["payload"]["event_type"],
            "review_cancelled",
        )