from django.test import SimpleTestCase

from ech.orders.exceptions import (
    OrderError,
    OrderNotFoundError,
    OrderPermissionDeniedError,
    EmptyOrderError,
    InvalidOrderAddressError,
    DuplicateOrderError,
    ProductNotAvailableError,
    InactiveProductError,
    InsufficientInventoryError,
    InvalidOrderStatusTransitionError,
    OrderCancellationNotAllowedError,
    OrderAlreadyCancelledError,
    OrderAlreadyShippedError,
    OrderAlreadyDeliveredError,
    InvalidPaymentStatusError,
    InvalidShippingStatusError,
)
from ech.orders.constants.messages import (
    MSG_EXCEPTIONS_ERROR_UNEXPECTED_ORDER,
    MSG_EXCEPTIONS_ERROR_ORDER_NOT_FOUND,
    MSG_EXCEPTIONS_ERROR_NO_PERMISSION,
    MSG_EXCEPTIONS_ERROR_ITEM_PROVIDED,
    MSG_EXCEPTIONS_ERROR_INVALID_ADDRESS,
    MSG_EXCEPTIONS_ERROR_DUPLICATED_ORDER,
    MSG_EXCEPTIONS_ERROR_PRODUCT_NOT_AVAILABLE,
    MSG_EXCEPTIONS_ERROR_PRODUCT_IS_INACTIVE,
    MSG_EXCEPTIONS_ERROR_INSUFFICIENT_INVENTORY,
    MSG_EXCEPTIONS_ERROR_INVALID_TRANSITION_STATUS,
    MSG_EXCEPTIONS_ERROR_ORDER_CANNOT_BE_CANCELLED,
    MSG_EXCEPTIONS_ERROR_ORDER_IS_ALREADY_CANCELLED,
    MSG_EXCEPTIONS_ERROR_ORDER_ALREADY_SHIPPED,
    MSG_EXCEPTIONS_ERROR_ORDER_ALREADY_DELIVERED,
    MSG_EXCEPTIONS_ERROR_INVALID_PAYMENT_STATUS,
    MSG_EXCEPTIONS_ERROR_INVALID_SHIPPING_STATUS,
)


class OrderErrorTestCase(SimpleTestCase):
    def test_order_error_uses_default_message_when_message_is_not_provided(self):
        exception = OrderError()

        self.assertEqual(exception.message, MSG_EXCEPTIONS_ERROR_UNEXPECTED_ORDER)
        self.assertEqual(str(exception), MSG_EXCEPTIONS_ERROR_UNEXPECTED_ORDER)

    def test_order_error_uses_custom_message_when_provided(self):
        exception = OrderError("Custom order error")

        self.assertEqual(exception.message, "Custom order error")
        self.assertEqual(str(exception), "Custom order error")

    def test_order_error_is_instance_of_exception(self):
        exception = OrderError()

        self.assertIsInstance(exception, Exception)

    def test_order_error_can_be_raised(self):
        with self.assertRaises(OrderError) as context:
            raise OrderError()

        self.assertEqual(str(context.exception), MSG_EXCEPTIONS_ERROR_UNEXPECTED_ORDER)


class OrderNotFoundErrorTestCase(SimpleTestCase):
    def test_order_not_found_error_inherits_from_order_error(self):
        exception = OrderNotFoundError()

        self.assertIsInstance(exception, OrderError)
        self.assertIsInstance(exception, Exception)

    def test_order_not_found_error_uses_default_message(self):
        exception = OrderNotFoundError()

        self.assertEqual(exception.message, MSG_EXCEPTIONS_ERROR_ORDER_NOT_FOUND)
        self.assertEqual(str(exception), MSG_EXCEPTIONS_ERROR_ORDER_NOT_FOUND)

    def test_order_not_found_error_accepts_custom_message(self):
        exception = OrderNotFoundError("Order with given id was not found")

        self.assertEqual(exception.message, "Order with given id was not found")
        self.assertEqual(str(exception), "Order with given id was not found")


class OrderPermissionDeniedErrorTestCase(SimpleTestCase):
    def test_order_permission_denied_error_inherits_from_order_error(self):
        exception = OrderPermissionDeniedError()

        self.assertIsInstance(exception, OrderError)

    def test_order_permission_denied_error_uses_default_message(self):
        exception = OrderPermissionDeniedError()

        self.assertEqual(exception.message, MSG_EXCEPTIONS_ERROR_NO_PERMISSION)
        self.assertEqual(str(exception), MSG_EXCEPTIONS_ERROR_NO_PERMISSION)

    def test_order_permission_denied_error_accepts_custom_message(self):
        exception = OrderPermissionDeniedError("Permission denied for this order")

        self.assertEqual(str(exception), "Permission denied for this order")


class EmptyOrderErrorTestCase(SimpleTestCase):
    def test_empty_order_error_inherits_from_order_error(self):
        exception = EmptyOrderError()

        self.assertIsInstance(exception, OrderError)

    def test_empty_order_error_uses_default_message(self):
        exception = EmptyOrderError()

        self.assertEqual(exception.message, MSG_EXCEPTIONS_ERROR_ITEM_PROVIDED)
        self.assertEqual(str(exception), MSG_EXCEPTIONS_ERROR_ITEM_PROVIDED)

    def test_empty_order_error_accepts_custom_message(self):
        exception = EmptyOrderError("Cannot create order without items")

        self.assertEqual(str(exception), "Cannot create order without items")


class InvalidOrderAddressErrorTestCase(SimpleTestCase):
    def test_invalid_order_address_error_inherits_from_order_error(self):
        exception = InvalidOrderAddressError()

        self.assertIsInstance(exception, OrderError)

    def test_invalid_order_address_error_uses_default_message(self):
        exception = InvalidOrderAddressError()

        self.assertEqual(exception.message, MSG_EXCEPTIONS_ERROR_INVALID_ADDRESS)
        self.assertEqual(str(exception), MSG_EXCEPTIONS_ERROR_INVALID_ADDRESS)

    def test_invalid_order_address_error_accepts_custom_message(self):
        exception = InvalidOrderAddressError("Provided address is invalid")

        self.assertEqual(str(exception), "Provided address is invalid")


class DuplicateOrderErrorTestCase(SimpleTestCase):
    def test_duplicate_order_error_inherits_from_order_error(self):
        exception = DuplicateOrderError()

        self.assertIsInstance(exception, OrderError)

    def test_duplicate_order_error_uses_default_message(self):
        exception = DuplicateOrderError()

        self.assertEqual(exception.message, MSG_EXCEPTIONS_ERROR_DUPLICATED_ORDER)
        self.assertEqual(str(exception), MSG_EXCEPTIONS_ERROR_DUPLICATED_ORDER)

    def test_duplicate_order_error_accepts_custom_message(self):
        exception = DuplicateOrderError("Duplicate order detected")

        self.assertEqual(str(exception), "Duplicate order detected")


class ProductNotAvailableErrorTestCase(SimpleTestCase):
    def test_product_not_available_error_inherits_from_order_error(self):
        exception = ProductNotAvailableError()

        self.assertIsInstance(exception, OrderError)

    def test_product_not_available_error_uses_default_message(self):
        exception = ProductNotAvailableError()

        self.assertEqual(exception.message, MSG_EXCEPTIONS_ERROR_PRODUCT_NOT_AVAILABLE)
        self.assertEqual(str(exception), MSG_EXCEPTIONS_ERROR_PRODUCT_NOT_AVAILABLE)

    def test_product_not_available_error_accepts_custom_message(self):
        exception = ProductNotAvailableError("Requested product is not available")

        self.assertEqual(str(exception), "Requested product is not available")


class InactiveProductErrorTestCase(SimpleTestCase):
    def test_inactive_product_error_inherits_from_order_error(self):
        exception = InactiveProductError()

        self.assertIsInstance(exception, OrderError)

    def test_inactive_product_error_uses_default_message(self):
        exception = InactiveProductError()

        self.assertEqual(exception.message, MSG_EXCEPTIONS_ERROR_PRODUCT_IS_INACTIVE)
        self.assertEqual(str(exception), MSG_EXCEPTIONS_ERROR_PRODUCT_IS_INACTIVE)

    def test_inactive_product_error_accepts_custom_message(self):
        exception = InactiveProductError("Product is inactive")

        self.assertEqual(str(exception), "Product is inactive")


class InsufficientInventoryErrorTestCase(SimpleTestCase):
    def test_insufficient_inventory_error_inherits_from_order_error(self):
        exception = InsufficientInventoryError()

        self.assertIsInstance(exception, OrderError)

    def test_insufficient_inventory_error_uses_default_message(self):
        exception = InsufficientInventoryError()

        self.assertEqual(exception.message, MSG_EXCEPTIONS_ERROR_INSUFFICIENT_INVENTORY)
        self.assertEqual(str(exception), MSG_EXCEPTIONS_ERROR_INSUFFICIENT_INVENTORY)

    def test_insufficient_inventory_error_accepts_custom_message(self):
        exception = InsufficientInventoryError("Insufficient inventory for requested quantity")

        self.assertEqual(str(exception), "Insufficient inventory for requested quantity")


class InvalidOrderStatusTransitionErrorTestCase(SimpleTestCase):
    def test_invalid_order_status_transition_error_inherits_from_order_error(self):
        exception = InvalidOrderStatusTransitionError()

        self.assertIsInstance(exception, OrderError)

    def test_invalid_order_status_transition_error_uses_default_message(self):
        exception = InvalidOrderStatusTransitionError()

        self.assertEqual(exception.message, MSG_EXCEPTIONS_ERROR_INVALID_TRANSITION_STATUS)
        self.assertEqual(str(exception), MSG_EXCEPTIONS_ERROR_INVALID_TRANSITION_STATUS)

    def test_invalid_order_status_transition_error_accepts_custom_message(self):
        exception = InvalidOrderStatusTransitionError("Invalid order status transition")

        self.assertEqual(str(exception), "Invalid order status transition")


class OrderCancellationNotAllowedErrorTestCase(SimpleTestCase):
    def test_order_cancellation_not_allowed_error_inherits_from_order_error(self):
        exception = OrderCancellationNotAllowedError()

        self.assertIsInstance(exception, OrderError)

    def test_order_cancellation_not_allowed_error_uses_default_message(self):
        exception = OrderCancellationNotAllowedError()

        self.assertEqual(exception.message, MSG_EXCEPTIONS_ERROR_ORDER_CANNOT_BE_CANCELLED)
        self.assertEqual(str(exception), MSG_EXCEPTIONS_ERROR_ORDER_CANNOT_BE_CANCELLED)

    def test_order_cancellation_not_allowed_error_accepts_custom_message(self):
        exception = OrderCancellationNotAllowedError("Order cannot be cancelled in current state")

        self.assertEqual(str(exception), "Order cannot be cancelled in current state")


class OrderAlreadyCancelledErrorTestCase(SimpleTestCase):
    def test_order_already_cancelled_error_inherits_from_order_error(self):
        exception = OrderAlreadyCancelledError()

        self.assertIsInstance(exception, OrderError)

    def test_order_already_cancelled_error_uses_default_message(self):
        exception = OrderAlreadyCancelledError()

        self.assertEqual(exception.message, MSG_EXCEPTIONS_ERROR_ORDER_IS_ALREADY_CANCELLED)
        self.assertEqual(str(exception), MSG_EXCEPTIONS_ERROR_ORDER_IS_ALREADY_CANCELLED)

    def test_order_already_cancelled_error_accepts_custom_message(self):
        exception = OrderAlreadyCancelledError("Order is already cancelled")

        self.assertEqual(str(exception), "Order is already cancelled")


class OrderAlreadyShippedErrorTestCase(SimpleTestCase):
    def test_order_already_shipped_error_inherits_from_order_error(self):
        exception = OrderAlreadyShippedError()

        self.assertIsInstance(exception, OrderError)

    def test_order_already_shipped_error_uses_default_message(self):
        exception = OrderAlreadyShippedError()

        self.assertEqual(exception.message, MSG_EXCEPTIONS_ERROR_ORDER_ALREADY_SHIPPED)
        self.assertEqual(str(exception), MSG_EXCEPTIONS_ERROR_ORDER_ALREADY_SHIPPED)

    def test_order_already_shipped_error_accepts_custom_message(self):
        exception = OrderAlreadyShippedError("Order has already been shipped")

        self.assertEqual(str(exception), "Order has already been shipped")


class OrderAlreadyDeliveredErrorTestCase(SimpleTestCase):
    def test_order_already_delivered_error_inherits_from_order_error(self):
        exception = OrderAlreadyDeliveredError()

        self.assertIsInstance(exception, OrderError)

    def test_order_already_delivered_error_uses_default_message(self):
        exception = OrderAlreadyDeliveredError()

        self.assertEqual(exception.message, MSG_EXCEPTIONS_ERROR_ORDER_ALREADY_DELIVERED)
        self.assertEqual(str(exception), MSG_EXCEPTIONS_ERROR_ORDER_ALREADY_DELIVERED)

    def test_order_already_delivered_error_accepts_custom_message(self):
        exception = OrderAlreadyDeliveredError("Order has already been delivered")

        self.assertEqual(str(exception), "Order has already been delivered")


class InvalidPaymentStatusErrorTestCase(SimpleTestCase):
    def test_invalid_payment_status_error_inherits_from_order_error(self):
        exception = InvalidPaymentStatusError()

        self.assertIsInstance(exception, OrderError)

    def test_invalid_payment_status_error_uses_default_message(self):
        exception = InvalidPaymentStatusError()

        self.assertEqual(exception.message, MSG_EXCEPTIONS_ERROR_INVALID_PAYMENT_STATUS)
        self.assertEqual(str(exception), MSG_EXCEPTIONS_ERROR_INVALID_PAYMENT_STATUS)

    def test_invalid_payment_status_error_accepts_custom_message(self):
        exception = InvalidPaymentStatusError("Invalid payment status for requested operation")

        self.assertEqual(str(exception), "Invalid payment status for requested operation")


class InvalidShippingStatusErrorTestCase(SimpleTestCase):
    def test_invalid_shipping_status_error_inherits_from_order_error(self):
        exception = InvalidShippingStatusError()

        self.assertIsInstance(exception, OrderError)

    def test_invalid_shipping_status_error_uses_default_message(self):
        exception = InvalidShippingStatusError()

        self.assertEqual(exception.message, MSG_EXCEPTIONS_ERROR_INVALID_SHIPPING_STATUS)
        self.assertEqual(str(exception), MSG_EXCEPTIONS_ERROR_INVALID_SHIPPING_STATUS)

    def test_invalid_shipping_status_error_accepts_custom_message(self):
        exception = InvalidShippingStatusError("Invalid shipping status for requested operation")

        self.assertEqual(str(exception), "Invalid shipping status for requested operation")