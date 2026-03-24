from django.test import SimpleTestCase

from ech.shipping.constants.messages import (
    SHIPMENT_NOT_FOUND,
    SHIPMENT_ALREADY_EXISTS,
    SHIPMENT_ACCESS_DENIED,
    SHIPMENT_UPDATE_NOT_ALLOWED,
    INVALID_SHIPMENT_STATUS_TRANSITION,
    SHIPMENT_ALREADY_DELIVERED,
    SHIPMENT_ALREADY_CANCELLED,
    SHIPMENT_CANCELLATION_NOT_ALLOWED,
    INVALID_SHIPPING_ADDRESS,
    TRACKING_CODE_REQUIRED,
    INVALID_TRACKING_EVENT,
)
from ech.shipping.exceptions import (
    ShippingException,
    ShipmentNotFoundException,
    ShipmentAccessDeniedException,
    ShipmentAlreadyExistsException,
    InvalidShippingAddressException,
    ShipmentUpdateNotAllowedException,
    InvalidShipmentStatusTransitionException,
    ShipmentAlreadyDeliveredException,
    ShipmentAlreadyCancelledException,
    ShipmentCancellationNotAllowedException,
    TrackingCodeRequiredException,
    InvalidTrackingEventException,
)


class ShippingExceptionTestCase(SimpleTestCase):
    def test_shipping_exception_inherits_from_exception(self):
        """Inherit the base shipping exception from Python Exception."""
        self.assertTrue(issubclass(ShippingException, Exception))

    def test_shipping_exception_accepts_custom_message(self):
        """Store a custom message in the base shipping exception."""
        exception = ShippingException("Custom shipping error")

        self.assertEqual(str(exception), "Custom shipping error")


class ShipmentNotFoundExceptionTestCase(SimpleTestCase):
    def test_shipment_not_found_exception_inherits_from_shipping_exception(self):
        """Inherit shipment not found exception from ShippingException."""
        self.assertTrue(issubclass(ShipmentNotFoundException, ShippingException))

    def test_shipment_not_found_exception_uses_default_message(self):
        """Use the default shipment not found message."""
        exception = ShipmentNotFoundException()

        self.assertEqual(str(exception), SHIPMENT_NOT_FOUND)

    def test_shipment_not_found_exception_accepts_custom_message(self):
        """Allow a custom message for shipment not found exception."""
        exception = ShipmentNotFoundException("Custom not found message")

        self.assertEqual(str(exception), "Custom not found message")


class ShipmentAccessDeniedExceptionTestCase(SimpleTestCase):
    def test_shipment_access_denied_exception_inherits_from_shipping_exception(self):
        """Inherit shipment access denied exception from ShippingException."""
        self.assertTrue(issubclass(ShipmentAccessDeniedException, ShippingException))

    def test_shipment_access_denied_exception_uses_default_message(self):
        """Use the default shipment access denied message."""
        exception = ShipmentAccessDeniedException()

        self.assertEqual(str(exception), SHIPMENT_ACCESS_DENIED)

    def test_shipment_access_denied_exception_accepts_custom_message(self):
        """Allow a custom message for shipment access denied exception."""
        exception = ShipmentAccessDeniedException("Custom access denied message")

        self.assertEqual(str(exception), "Custom access denied message")


class ShipmentAlreadyExistsExceptionTestCase(SimpleTestCase):
    def test_shipment_already_exists_exception_inherits_from_shipping_exception(self):
        """Inherit shipment already exists exception from ShippingException."""
        self.assertTrue(issubclass(ShipmentAlreadyExistsException, ShippingException))

    def test_shipment_already_exists_exception_uses_default_message(self):
        """Use the default shipment already exists message."""
        exception = ShipmentAlreadyExistsException()

        self.assertEqual(str(exception), SHIPMENT_ALREADY_EXISTS)

    def test_shipment_already_exists_exception_accepts_custom_message(self):
        """Allow a custom message for shipment already exists exception."""
        exception = ShipmentAlreadyExistsException("Custom already exists message")

        self.assertEqual(str(exception), "Custom already exists message")


class InvalidShippingAddressExceptionTestCase(SimpleTestCase):
    def test_invalid_shipping_address_exception_inherits_from_shipping_exception(self):
        """Inherit invalid shipping address exception from ShippingException."""
        self.assertTrue(issubclass(InvalidShippingAddressException, ShippingException))

    def test_invalid_shipping_address_exception_uses_default_message(self):
        """Use the default invalid shipping address message."""
        exception = InvalidShippingAddressException()

        self.assertEqual(str(exception), INVALID_SHIPPING_ADDRESS)

    def test_invalid_shipping_address_exception_accepts_custom_message(self):
        """Allow a custom message for invalid shipping address exception."""
        exception = InvalidShippingAddressException("Custom invalid address message")

        self.assertEqual(str(exception), "Custom invalid address message")


class ShipmentUpdateNotAllowedExceptionTestCase(SimpleTestCase):
    def test_shipment_update_not_allowed_exception_inherits_from_shipping_exception(self):
        """Inherit shipment update not allowed exception from ShippingException."""
        self.assertTrue(issubclass(ShipmentUpdateNotAllowedException, ShippingException))

    def test_shipment_update_not_allowed_exception_uses_default_message(self):
        """Use the default shipment update not allowed message."""
        exception = ShipmentUpdateNotAllowedException()

        self.assertEqual(str(exception), SHIPMENT_UPDATE_NOT_ALLOWED)

    def test_shipment_update_not_allowed_exception_accepts_custom_message(self):
        """Allow a custom message for shipment update not allowed exception."""
        exception = ShipmentUpdateNotAllowedException("Custom update not allowed message")

        self.assertEqual(str(exception), "Custom update not allowed message")


class InvalidShipmentStatusTransitionExceptionTestCase(SimpleTestCase):
    def test_invalid_shipment_status_transition_exception_inherits_from_shipping_exception(self):
        """Inherit invalid shipment status transition exception from ShippingException."""
        self.assertTrue(
            issubclass(InvalidShipmentStatusTransitionException, ShippingException)
        )

    def test_invalid_shipment_status_transition_exception_uses_default_message(self):
        """Use the default invalid shipment status transition message."""
        exception = InvalidShipmentStatusTransitionException()

        self.assertEqual(str(exception), INVALID_SHIPMENT_STATUS_TRANSITION)

    def test_invalid_shipment_status_transition_exception_accepts_custom_message(self):
        """Allow a custom message for invalid shipment status transition exception."""
        exception = InvalidShipmentStatusTransitionException(
            "Custom invalid status transition message"
        )

        self.assertEqual(str(exception), "Custom invalid status transition message")


class ShipmentAlreadyDeliveredExceptionTestCase(SimpleTestCase):
    def test_shipment_already_delivered_exception_inherits_from_shipping_exception(self):
        """Inherit shipment already delivered exception from ShippingException."""
        self.assertTrue(issubclass(ShipmentAlreadyDeliveredException, ShippingException))

    def test_shipment_already_delivered_exception_uses_default_message(self):
        """Use the default shipment already delivered message."""
        exception = ShipmentAlreadyDeliveredException()

        self.assertEqual(str(exception), SHIPMENT_ALREADY_DELIVERED)

    def test_shipment_already_delivered_exception_accepts_custom_message(self):
        """Allow a custom message for shipment already delivered exception."""
        exception = ShipmentAlreadyDeliveredException(
            "Custom already delivered message"
        )

        self.assertEqual(str(exception), "Custom already delivered message")


class ShipmentAlreadyCancelledExceptionTestCase(SimpleTestCase):
    def test_shipment_already_cancelled_exception_inherits_from_shipping_exception(self):
        """Inherit shipment already cancelled exception from ShippingException."""
        self.assertTrue(issubclass(ShipmentAlreadyCancelledException, ShippingException))

    def test_shipment_already_cancelled_exception_uses_default_message(self):
        """Use the default shipment already cancelled message."""
        exception = ShipmentAlreadyCancelledException()

        self.assertEqual(str(exception), SHIPMENT_ALREADY_CANCELLED)

    def test_shipment_already_cancelled_exception_accepts_custom_message(self):
        """Allow a custom message for shipment already cancelled exception."""
        exception = ShipmentAlreadyCancelledException(
            "Custom already cancelled message"
        )

        self.assertEqual(str(exception), "Custom already cancelled message")


class ShipmentCancellationNotAllowedExceptionTestCase(SimpleTestCase):
    def test_shipment_cancellation_not_allowed_exception_inherits_from_shipping_exception(self):
        """Inherit shipment cancellation not allowed exception from ShippingException."""
        self.assertTrue(
            issubclass(ShipmentCancellationNotAllowedException, ShippingException)
        )

    def test_shipment_cancellation_not_allowed_exception_uses_default_message(self):
        """Use the default shipment cancellation not allowed message."""
        exception = ShipmentCancellationNotAllowedException()

        self.assertEqual(str(exception), SHIPMENT_CANCELLATION_NOT_ALLOWED)

    def test_shipment_cancellation_not_allowed_exception_accepts_custom_message(self):
        """Allow a custom message for shipment cancellation not allowed exception."""
        exception = ShipmentCancellationNotAllowedException(
            "Custom cancellation not allowed message"
        )

        self.assertEqual(str(exception), "Custom cancellation not allowed message")


class TrackingCodeRequiredExceptionTestCase(SimpleTestCase):
    def test_tracking_code_required_exception_inherits_from_shipping_exception(self):
        """Inherit tracking code required exception from ShippingException."""
        self.assertTrue(issubclass(TrackingCodeRequiredException, ShippingException))

    def test_tracking_code_required_exception_uses_default_message(self):
        """Use the default tracking code required message."""
        exception = TrackingCodeRequiredException()

        self.assertEqual(str(exception), TRACKING_CODE_REQUIRED)

    def test_tracking_code_required_exception_accepts_custom_message(self):
        """Allow a custom message for tracking code required exception."""
        exception = TrackingCodeRequiredException("Custom tracking required message")

        self.assertEqual(str(exception), "Custom tracking required message")


class InvalidTrackingEventExceptionTestCase(SimpleTestCase):
    def test_invalid_tracking_event_exception_inherits_from_shipping_exception(self):
        """Inherit invalid tracking event exception from ShippingException."""
        self.assertTrue(issubclass(InvalidTrackingEventException, ShippingException))

    def test_invalid_tracking_event_exception_uses_default_message(self):
        """Use the default invalid tracking event message."""
        exception = InvalidTrackingEventException()

        self.assertEqual(str(exception), INVALID_TRACKING_EVENT)

    def test_invalid_tracking_event_exception_accepts_custom_message(self):
        """Allow a custom message for invalid tracking event exception."""
        exception = InvalidTrackingEventException("Custom invalid tracking event message")

        self.assertEqual(str(exception), "Custom invalid tracking event message")