import uuid
from decimal import Decimal

from django.db import IntegrityError, transaction

from ech.orders.models import Order
from ech.payments.exceptions import (
    DuplicateIdempotencyKey,
    DuplicatePaymentReference,
    PaymentAmountMismatch,
    PaymentCreationNotAllowed,
    PaymentCustomerMismatch,
)
from ech.payments.models import (
    Payment, 
    PaymentLifecycle,
)

from ech.payments.domain_events.dispatcher import payment_event_dispatcher
from ech.payments.domain_events.events import PaymentCreatedEvent

from ech.payments.services.payment_log_service import PaymentLogService

from ech.payments.constants.messages import (
    MSG_EXCEPTIONS_ERROR_PAYMENT_REFERENCE_ALREADY_EXISTS,
    MSG_EXCEPTIONS_ERROR_IDEMPOTENCY_KEY_ALREADY_BEEN_USED,
    MSG_EXCEPTIONS_ERROR_PAYMENT_CUSTOMER_DOES_NOT_MATCH,
    MSG_EXCEPTIONS_ERROR_PAYMENT_AMOUNT_DOES_NOT_MATCH,
    MSG_SERVICE_ERROR_PAYMENT_CREATION_IS_NOT_ALLOWED_FOR_CANCELLED_OR_REFUNDED_ORDERS,
    MSG_SERVICE_ERROR_PAYMENT_CREATION_IS_NOT_ALLOWED_FOR_ACTIVE_FLOW_ORDERS,
    MSG_SERVICE_ERROR_PAYMENT_CREATION_IS_NOT_ALLOWED_FOR_ORDERS_WITHOUT_TOTALS,
    MSG_SERVICE_ERROR_PAYMENT_ALREADY_EXISTS_FOR_THIS_ORDER,
)


class PaymentCreationService:
    """
    Service responsible for creating payments.

    Responsibilities:
        - validate payment creation eligibility
        - enforce order/payment consistency
        - enforce idempotency
        - generate payment reference
        - create payment lifecycle
        - register initial payment event
    """

    PAYMENT_REFERENCE_PREFIX = "PAY"

    @classmethod
    @transaction.atomic
    def create_payment(
        cls,
        *,
        order: Order,
        method: str,
        created_by=None,
        payment_reference: str | None = None,
        idempotency_key=None,
        gateway_name: str = "",
        gateway_payment_id: str = "",
        gateway_customer_id: str = "",
        metadata: dict | None = None,
    ) -> Payment:
        """
        Create and return a payment for the given order.

        Rules enforced:
            - order must be eligible for payment creation
            - order must have totals
            - order must not already have a payment
            - idempotency key cannot be reused
            - payment amount must match order grand total
            - payment customer must match order customer
        """

        cls._validate_order_eligibility(order=order)
        cls._validate_order_has_totals(order=order)
        cls._validate_order_has_no_payment(order=order)

        if idempotency_key is not None:
            cls._validate_idempotency_key(idempotency_key=idempotency_key)

        amount = cls._get_order_amount(order=order)
        currency = cls._get_order_currency(order=order)
        customer = order.customer

        payment_reference = payment_reference or cls._generate_payment_reference()

        cls._validate_payment_reference_uniqueness(
            payment_reference=payment_reference
        )

        try:
            payment = Payment.objects.create(
                order=order,
                customer=customer,
                payment_reference=payment_reference,
                method=method,
                status=Payment.PAYMENT_STATUS_PENDING,
                amount=amount,
                refunded_amount=Decimal("0.00"),
                currency=currency,
                gateway_name=gateway_name,
                gateway_payment_id=gateway_payment_id,
                gateway_customer_id=gateway_customer_id,
                idempotency_key=idempotency_key,
                metadata=metadata or {},
            )
        except IntegrityError as exc:
            if idempotency_key is not None and Payment.objects.filter(
                idempotency_key=idempotency_key
            ).exists():
                raise DuplicateIdempotencyKey(MSG_EXCEPTIONS_ERROR_IDEMPOTENCY_KEY_ALREADY_BEEN_USED) from exc

            if Payment.objects.filter(
                payment_reference=payment_reference
            ).exists():
                raise DuplicatePaymentReference(MSG_EXCEPTIONS_ERROR_PAYMENT_REFERENCE_ALREADY_EXISTS) from exc

            raise

        cls._validate_payment_consistency(
            payment=payment,
            order=order,
            expected_amount=amount,
        )

        PaymentLifecycle.objects.create(payment=payment)

        PaymentLogService.log_created(
            payment=payment,
            performed_by=created_by,
            metadata={
                "order_id": str(order.id),
                "customer_id": str(customer.id),
                "method": payment.method,
                "amount": str(payment.amount),
                "currency": payment.currency,
                **(metadata or {}),
            },
        )

        payment_event_dispatcher.dispatch(
            PaymentCreatedEvent(
                payment_id=payment.id,
                order_id=order.id,
                customer_id=customer.id,
                payment_reference=payment.payment_reference,
                method=payment.method,
                status=payment.status,
                amount=str(payment.amount),
                currency=payment.currency,
                metadata=metadata or {},
            )
        )

        return payment

    @staticmethod
    def _validate_order_eligibility(*, order: Order) -> None:
        """
        Validate whether the order is eligible for payment creation.
        """

        if order.status in {
            Order.ORDER_STATUS_CANCELLED,
            Order.ORDER_STATUS_REFUNDED,
        }:
            raise PaymentCreationNotAllowed(MSG_SERVICE_ERROR_PAYMENT_CREATION_IS_NOT_ALLOWED_FOR_CANCELLED_OR_REFUNDED_ORDERS)

        if order.payment_status in {
            Order.PAYMENT_STATUS_PROCESSING,
            Order.PAYMENT_STATUS_AUTHORIZED,
            Order.PAYMENT_STATUS_CAPTURED,
            Order.PAYMENT_STATUS_PARTIALLY_REFUNDED,
            Order.PAYMENT_STATUS_REFUNDED,
        }:
            raise PaymentCreationNotAllowed(MSG_SERVICE_ERROR_PAYMENT_CREATION_IS_NOT_ALLOWED_FOR_ACTIVE_FLOW_ORDERS)

    @staticmethod
    def _validate_order_has_totals(*, order: Order) -> None:
        """
        Validate that the order has totals available.
        """

        if not hasattr(order, "totals"):
            raise PaymentCreationNotAllowed(MSG_SERVICE_ERROR_PAYMENT_CREATION_IS_NOT_ALLOWED_FOR_ORDERS_WITHOUT_TOTALS)

    @staticmethod
    def _validate_order_has_no_payment(*, order: Order) -> None:
        """
        Validate that the order does not already have a payment.

        This rule matches the current Payment model, where Payment.order
        is a OneToOneField.
        """

        if hasattr(order, "payment"):
            raise PaymentCreationNotAllowed(MSG_SERVICE_ERROR_PAYMENT_ALREADY_EXISTS_FOR_THIS_ORDER)

    @staticmethod
    def _validate_idempotency_key(*, idempotency_key) -> None:
        """
        Validate that the idempotency key has not already been used.
        """

        if Payment.objects.filter(idempotency_key=idempotency_key).exists():
            raise DuplicateIdempotencyKey(MSG_EXCEPTIONS_ERROR_IDEMPOTENCY_KEY_ALREADY_BEEN_USED)

    @staticmethod
    def _validate_payment_reference_uniqueness(
        *,
        payment_reference: str,
    ) -> None:
        """
        Validate that the payment reference is unique.
        """

        if Payment.objects.filter(payment_reference=payment_reference).exists():
            raise DuplicatePaymentReference(MSG_EXCEPTIONS_ERROR_PAYMENT_REFERENCE_ALREADY_EXISTS)

    @staticmethod
    def _get_order_amount(*, order: Order) -> Decimal:
        """
        Return the order grand total as the payment amount.
        """

        return order.totals.grand_total

    @staticmethod
    def _get_order_currency(*, order: Order) -> str:
        """
        Return the order currency.
        """

        return order.currency

    @classmethod
    def _generate_payment_reference(cls) -> str:
        """
        Generate a unique public payment reference.
        """

        return f"{cls.PAYMENT_REFERENCE_PREFIX}-{uuid.uuid4().hex[:12].upper()}"

    @staticmethod
    def _validate_payment_consistency(
        *,
        payment: Payment,
        order: Order,
        expected_amount: Decimal,
    ) -> None:
        """
        Validate created payment consistency against the related order.
        """

        if payment.customer_id != order.customer_id:
            raise PaymentCustomerMismatch(MSG_EXCEPTIONS_ERROR_PAYMENT_CUSTOMER_DOES_NOT_MATCH)

        if payment.amount != expected_amount:
            raise PaymentAmountMismatch(MSG_EXCEPTIONS_ERROR_PAYMENT_AMOUNT_DOES_NOT_MATCH)