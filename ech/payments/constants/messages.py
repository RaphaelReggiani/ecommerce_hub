# =========================
# ERRORS MESSAGES
# =========================

MSG_ERROR_PAYMENT_NOT_FOUND_FOR_PROVIDED_ORDER = "Payment not found for the provided order."
MSG_ERROR_PAYMENT_LIFECYCLE_NOT_FOUND = "Payment lifecycle not found."

# =============================
# SERIALIZERS VALIDATION ERROR
# =============================


# ===================================
# DEFAULT ERROR MESSAGES
# ===================================

MSG_EXCEPTIONS_ERROR_UNEXPECTED_PAYMENT = "An unexpected payment error occurred."
MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_FOUND = "Payment not found."
MSG_EXCEPTIONS_ERROR_PERMISSION_DENIED_TO_PERFORM_PAYMENT = "You do not have permission to perform this payment action."
MSG_EXCEPTIONS_ERROR_PAYMENT_NOT_ALLOWED_FOR_ORDER = "Payment creation is not allowed for this order."
MSG_EXCEPTIONS_ERROR_PAYMENT_ALREADY_PROCESSED = "This payment has already been processed."
MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_PROCESSED = "This payment cannot be processed in its current state."
MSG_EXCEPTIONS_ERROR_PAYMENT_PROCESSING_FAILED = "Payment processing failed."
MSG_EXCEPTIONS_ERROR_INVALID_PAYMENT_TRANSITION = "Invalid payment status transition."
MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_CANCELLED = "This payment cannot be cancelled."
MSG_EXCEPTIONS_ERROR_PAYMENT_ALREADY_CANCELLED = "This payment has already been cancelled."
MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_REFUNDED = "This payment cannot be refunded."
MSG_EXCEPTIONS_ERROR_PAYMENT_ALREADY_REFUNDED = "This payment has already been fully refunded."
MSG_EXCEPTIONS_ERROR_PAYMENT_IS_NOT_REFUNDABLE = "This payment is not refundable."
MSG_EXCEPTIONS_ERROR_REFUND_AMOUNT_EXCEEDS_AVAILABLE_REFUNDABLE_BALANCE = "Refund amount exceeds the available refundable balance."
MSG_EXCEPTIONS_ERROR_INVALID_REFUND_AMOUNT = "Invalid refund amount."
MSG_EXCEPTIONS_ERROR_PAYMENT_TRANSACTION_NOT_FOUND = "Payment transaction not found."
MSG_EXCEPTIONS_ERROR_PAYMENT_TRANSACTION_NOT_ALLOWED = "This payment transaction is not allowed."
MSG_EXCEPTIONS_ERROR_PAYMENT_REFERENCE_ALREADY_EXISTS = "A payment with this reference already exists."
MSG_EXCEPTIONS_ERROR_IDEMPOTENCY_KEY_ALREADY_BEEN_USED = "This idempotency key has already been used."
MSG_EXCEPTIONS_ERROR_PAYMENT_DATA_DOES_NOT_MATCH = "Payment data does not match the related order."
MSG_EXCEPTIONS_ERROR_PAYMENT_CUSTOMER_DOES_NOT_MATCH = "Payment customer does not match the related order customer."
MSG_EXCEPTIONS_ERROR_PAYMENT_AMOUNT_DOES_NOT_MATCH = "Payment amount does not match the expected order total."
MSG_EXCEPTIONS_ERROR_REFUND_PROCESSING_FAILED = "Refund processing failed."
MSG_EXCEPTIONS_ERROR_PAYMENT_REFUND_NOT_FOUND = "Payment refund not found."
MSG_EXCEPTIONS_ERROR_REFUND_ALREADY_BEEN_PROCESSED = "This refund has already been processed."
MSG_EXCEPTIONS_ERROR_REFUND_ALREADY_BEEN_CANCELLED = "This refund has already been cancelled."
MSG_EXCEPTIONS_ERROR_PAYMENT_CANNOT_BE_CANCELLED_IN_ITS_STATE = "This refund cannot be cancelled in its current state."


# ===================================
# CREATION SERVICE ERROR MESSAGES
# ===================================

MSG_SERVICE_ERROR_PAYMENT_CREATION_IS_NOT_ALLOWED_FOR_CANCELLED_OR_REFUNDED_ORDERS = "Payment creation is not allowed for cancelled or refunded orders."
MSG_SERVICE_ERROR_PAYMENT_CREATION_IS_NOT_ALLOWED_FOR_ACTIVE_FLOW_ORDERS = "Payment creation is not allowed for orders with an active or completed payment flow."
MSG_SERVICE_ERROR_PAYMENT_CREATION_IS_NOT_ALLOWED_FOR_ORDERS_WITHOUT_TOTALS = "Payment creation is not allowed for orders without totals."
MSG_SERVICE_ERROR_PAYMENT_ALREADY_EXISTS_FOR_THIS_ORDER = "A payment already exists for this order."

# ===================================
# STATUS SERVICE ERROR MESSAGES
# ===================================

MSG_SERVICE_ERROR_ONLY_PAYMENTS_IN_PROCESSING_STATUS_CAN_BE_AUTHORIZED = "Only payments in processing status can be authorized."
MSG_SERVICE_ERROR_ONLY_PAYMENTS_IN_PROCESSING_OR_AUTHORIZED_CAN_BE_CAPTURED = "Only processing or authorized payments can be captured."
MSG_SERVICE_ERROR_ONLY_PROCESSING_PAYMENTS_CAN_BE_CHARGED = "Only pending or processing payments can be charged."
MSG_SERVICE_ERROR_PAYMENT_CANNOT_BE_MARKED_AS_FAILED = "This payment cannot be marked as failed from its current state."

# ===================================
# PROCESSING SERVICE ERROR MESSAGES
# ===================================

MSG_SERVICE_ERROR_PAYMENT_CANNOT_BE_CANCELLED_FROM_ITS_CURRENT_STATE = "This payment cannot be cancelled from its current state."

# ===================================
# REFUND SERVICE ERROR MESSAGES
# ===================================

MSG_SERVICE_ERROR_ONLY_CAPTURED_OR_PARTIALLY_REFUNDED_PAYMENTS_CAN_BE_REFUNDED = "Only captured or partially refunded payments can be refunded."
MSG_SERVICE_ERROR_REFUND_AMOUNT_MUST_BE_GREATER = "Refund amount must be greater than zero."
MSG_SERVICE_ERROR_REFUND_AMOUNT_EXCEEDS_REMAINING_REFUNDABLE_AMOUNT = "Refund amount exceeds remaining refundable amount."
MSG_SERVICE_ERROR_ONLY_PENDING_REFUNDS_CAN_BE_PROCESSED = "Only pending refunds can be processed."
MSG_SERVICE_ERROR_PROCESSED_REFUNDS_CANNOT_BE_MARKED_AS_FAILED = "Processed refunds cannot be marked as failed."
MSG_SERVICE_ERROR_CANCELLED_REFUNDS_CANNOT_BE_MARKED_AS_FAILED = "Cancelled refunds cannot be marked as failed."
MSG_SERVICE_ERROR_ONLY_PENDING_REFUNDS_CAN_BE_MARKED_AS_FAILED = "Only pending refunds can be marked as failed."
MSG_SERVICE_ERROR_PROCESSED_REFUNDS_CANNOT_BE_CANCELLED = "Processed refunds cannot be cancelled."
MSG_SERVICE_ERROR_ONLY_PENDING_REFUNDS_CAN_BE_CANCELLED = "Only pending refunds can be cancelled."
