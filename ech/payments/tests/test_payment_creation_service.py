from decimal import Decimal
from unittest.mock import patch
import uuid

from django.test import TestCase

from ech.orders.models import Order, OrderTotals
from ech.payments.constants.messages import (
    MSG_EXCEPTIONS_ERROR_IDEMPOTENCY_KEY_ALREADY_BEEN_USED,
    MSG_EXCEPTIONS_ERROR_PAYMENT_AMOUNT_DOES_NOT_MATCH,
    MSG_EXCEPTIONS_ERROR_PAYMENT_CUSTOMER_DOES_NOT_MATCH,
    MSG_EXCEPTIONS_ERROR_PAYMENT_REFERENCE_ALREADY_EXISTS,
    MSG_SERVICE_ERROR_PAYMENT_ALREADY_EXISTS_FOR_THIS_ORDER,
    MSG_SERVICE_ERROR_PAYMENT_CREATION_IS_NOT_ALLOWED_FOR_ACTIVE_FLOW_ORDERS,
    MSG_SERVICE_ERROR_PAYMENT_CREATION_IS_NOT_ALLOWED_FOR_CANCELLED_OR_REFUNDED_ORDERS,
    MSG_SERVICE_ERROR_PAYMENT_CREATION_IS_NOT_ALLOWED_FOR_ORDERS_WITHOUT_TOTALS,
)
from ech.payments.exceptions import (
    DuplicateIdempotencyKey,
    DuplicatePaymentReference,
    PaymentAmountMismatch,
    PaymentCreationNotAllowed,
    PaymentCustomerMismatch,
)
from ech.payments.models import Payment, PaymentLifecycle
from ech.payments.services.payment_creation_service import PaymentCreationService
from ech.users.models import CustomUser


class PaymentCreationServiceTestCase(TestCase):
    def setUp(self):
        self.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.other_customer = CustomUser.objects.create_user(
            email="other@test.com",
            password="StrongPassword123",
            user_name="Other Customer",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.actor = CustomUser.objects.create_user(
            email="actor@test.com",
            password="StrongPassword123",
            user_name="Actor",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.order = Order.objects.create(
            customer=self.customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
            currency="USD",
        )

        self.totals = OrderTotals.objects.create(
            order=self.order,
            subtotal=Decimal("100.00"),
            discount_total=Decimal("0.00"),
            tax_total=Decimal("0.00"),
            shipping_total=Decimal("0.00"),
            grand_total=Decimal("100.00"),
        )

    @patch("ech.payments.services.payment_creation_service.payment_event_dispatcher.dispatch")
    @patch("ech.payments.services.payment_creation_service.PaymentLogService.log_created")
    @patch(
        "ech.payments.services.payment_creation_service.PaymentCreationService._generate_payment_reference",
        return_value="PAY-GENERATED-001",
    )
    def test_create_payment_success(
        self,
        mock_generate_reference,
        mock_log_created,
        mock_dispatch,
    ):
        """Ensure service creates payment, lifecycle, log, and event successfully."""
        payment = PaymentCreationService.create_payment(
            order=self.order,
            method=Payment.PAYMENT_METHOD_PIX,
            created_by=self.actor,
            gateway_name="Stripe",
            gateway_payment_id="gw_123",
            gateway_customer_id="cust_123",
            metadata={"source": "test"},
        )

        self.assertEqual(payment.order, self.order)
        self.assertEqual(payment.customer, self.customer)
        self.assertEqual(payment.payment_reference, "PAY-GENERATED-001")
        self.assertEqual(payment.method, Payment.PAYMENT_METHOD_PIX)
        self.assertEqual(payment.status, Payment.PAYMENT_STATUS_PENDING)
        self.assertEqual(payment.amount, Decimal("100.00"))
        self.assertEqual(payment.refunded_amount, Decimal("0.00"))
        self.assertEqual(payment.currency, "USD")
        self.assertEqual(payment.gateway_name, "Stripe")
        self.assertEqual(payment.gateway_payment_id, "gw_123")
        self.assertEqual(payment.gateway_customer_id, "cust_123")
        self.assertEqual(payment.metadata, {"source": "test"})

        self.assertTrue(PaymentLifecycle.objects.filter(payment=payment).exists())

        mock_generate_reference.assert_called_once()
        mock_log_created.assert_called_once()
        mock_dispatch.assert_called_once()

    @patch("ech.payments.services.payment_creation_service.payment_event_dispatcher.dispatch")
    @patch("ech.payments.services.payment_creation_service.PaymentLogService.log_created")
    def test_create_payment_uses_explicit_payment_reference(
        self,
        mock_log_created,
        mock_dispatch,
    ):
        """Ensure service uses explicit payment reference when provided."""
        payment = PaymentCreationService.create_payment(
            order=self.order,
            method=Payment.PAYMENT_METHOD_CREDIT_CARD,
            payment_reference="PAY-CUSTOM-001",
        )

        self.assertEqual(payment.payment_reference, "PAY-CUSTOM-001")
        mock_log_created.assert_called_once()
        mock_dispatch.assert_called_once()

    def test_create_payment_raises_for_cancelled_order(self):
        """Ensure service blocks payment creation for cancelled orders."""
        self.order.status = Order.ORDER_STATUS_CANCELLED
        self.order.save(update_fields=["status"])

        with self.assertRaises(PaymentCreationNotAllowed) as context:
            PaymentCreationService.create_payment(
                order=self.order,
                method=Payment.PAYMENT_METHOD_PIX,
            )

        self.assertEqual(
            str(context.exception),
            MSG_SERVICE_ERROR_PAYMENT_CREATION_IS_NOT_ALLOWED_FOR_CANCELLED_OR_REFUNDED_ORDERS,
        )

    def test_create_payment_raises_for_refunded_order(self):
        """Ensure service blocks payment creation for refunded orders."""
        self.order.status = Order.ORDER_STATUS_REFUNDED
        self.order.save(update_fields=["status"])

        with self.assertRaises(PaymentCreationNotAllowed) as context:
            PaymentCreationService.create_payment(
                order=self.order,
                method=Payment.PAYMENT_METHOD_PIX,
            )

        self.assertEqual(
            str(context.exception),
            MSG_SERVICE_ERROR_PAYMENT_CREATION_IS_NOT_ALLOWED_FOR_CANCELLED_OR_REFUNDED_ORDERS,
        )

    def test_create_payment_raises_for_processing_payment_flow(self):
        """Ensure service blocks payment creation for orders already in active payment flow."""
        self.order.payment_status = Order.PAYMENT_STATUS_PROCESSING
        self.order.save(update_fields=["payment_status"])

        with self.assertRaises(PaymentCreationNotAllowed) as context:
            PaymentCreationService.create_payment(
                order=self.order,
                method=Payment.PAYMENT_METHOD_PIX,
            )

        self.assertEqual(
            str(context.exception),
            MSG_SERVICE_ERROR_PAYMENT_CREATION_IS_NOT_ALLOWED_FOR_ACTIVE_FLOW_ORDERS,
        )

    def test_create_payment_raises_for_authorized_payment_flow(self):
        """Ensure service blocks payment creation for authorized orders."""
        self.order.payment_status = Order.PAYMENT_STATUS_AUTHORIZED
        self.order.save(update_fields=["payment_status"])

        with self.assertRaises(PaymentCreationNotAllowed):
            PaymentCreationService.create_payment(
                order=self.order,
                method=Payment.PAYMENT_METHOD_PIX,
            )

    def test_create_payment_raises_for_captured_payment_flow(self):
        """Ensure service blocks payment creation for captured orders."""
        self.order.payment_status = Order.PAYMENT_STATUS_CAPTURED
        self.order.save(update_fields=["payment_status"])

        with self.assertRaises(PaymentCreationNotAllowed):
            PaymentCreationService.create_payment(
                order=self.order,
                method=Payment.PAYMENT_METHOD_PIX,
            )

    def test_create_payment_raises_for_partially_refunded_payment_flow(self):
        """Ensure service blocks payment creation for partially refunded orders."""
        self.order.payment_status = Order.PAYMENT_STATUS_PARTIALLY_REFUNDED
        self.order.save(update_fields=["payment_status"])

        with self.assertRaises(PaymentCreationNotAllowed):
            PaymentCreationService.create_payment(
                order=self.order,
                method=Payment.PAYMENT_METHOD_PIX,
            )

    def test_create_payment_raises_for_refunded_payment_flow(self):
        """Ensure service blocks payment creation for refunded orders with completed payment flow."""
        self.order.payment_status = Order.PAYMENT_STATUS_REFUNDED
        self.order.save(update_fields=["payment_status"])

        with self.assertRaises(PaymentCreationNotAllowed):
            PaymentCreationService.create_payment(
                order=self.order,
                method=Payment.PAYMENT_METHOD_PIX,
            )

    def test_create_payment_raises_when_order_has_no_totals(self):
        """Ensure service blocks payment creation when order totals do not exist."""
        order_without_totals = Order.objects.create(
            customer=self.customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
        )

        with self.assertRaises(PaymentCreationNotAllowed) as context:
            PaymentCreationService.create_payment(
                order=order_without_totals,
                method=Payment.PAYMENT_METHOD_PIX,
            )

        self.assertEqual(
            str(context.exception),
            MSG_SERVICE_ERROR_PAYMENT_CREATION_IS_NOT_ALLOWED_FOR_ORDERS_WITHOUT_TOTALS,
        )

    def test_create_payment_raises_when_order_already_has_payment(self):
        """Ensure service blocks payment creation when order already has a payment."""
        Payment.objects.create(
            order=self.order,
            customer=self.customer,
            payment_reference="PAY-EXISTING-001",
            method=Payment.PAYMENT_METHOD_PIX,
            status=Payment.PAYMENT_STATUS_PENDING,
            amount=Decimal("100.00"),
        )

        with self.assertRaises(PaymentCreationNotAllowed) as context:
            PaymentCreationService.create_payment(
                order=self.order,
                method=Payment.PAYMENT_METHOD_PIX,
            )

        self.assertEqual(
            str(context.exception),
            MSG_SERVICE_ERROR_PAYMENT_ALREADY_EXISTS_FOR_THIS_ORDER,
        )

    def test_create_payment_raises_for_duplicate_idempotency_key_precheck(self):
        """Ensure service blocks reused idempotency key before creating payment."""
        idempotency_key = uuid.uuid4()

        Payment.objects.create(
            order=Order.objects.create(
                customer=self.other_customer,
                status=Order.ORDER_STATUS_PENDING,
                payment_status=Order.PAYMENT_STATUS_PENDING,
                shipping_status=Order.SHIPPING_STATUS_PENDING,
            ),
            customer=self.other_customer,
            payment_reference="PAY-IDEMP-EXISTING",
            method=Payment.PAYMENT_METHOD_PIX,
            status=Payment.PAYMENT_STATUS_PENDING,
            amount=Decimal("50.00"),
            idempotency_key=idempotency_key,
        )

        with self.assertRaises(DuplicateIdempotencyKey) as context:
            PaymentCreationService.create_payment(
                order=self.order,
                method=Payment.PAYMENT_METHOD_PIX,
                idempotency_key=idempotency_key,
            )

        self.assertEqual(
            str(context.exception),
            MSG_EXCEPTIONS_ERROR_IDEMPOTENCY_KEY_ALREADY_BEEN_USED,
        )

    def test_create_payment_raises_for_duplicate_payment_reference_precheck(self):
        """Ensure service blocks reused payment reference before creating payment."""
        Payment.objects.create(
            order=Order.objects.create(
                customer=self.other_customer,
                status=Order.ORDER_STATUS_PENDING,
                payment_status=Order.PAYMENT_STATUS_PENDING,
                shipping_status=Order.SHIPPING_STATUS_PENDING,
            ),
            customer=self.other_customer,
            payment_reference="PAY-DUPLICATE-001",
            method=Payment.PAYMENT_METHOD_PIX,
            status=Payment.PAYMENT_STATUS_PENDING,
            amount=Decimal("50.00"),
        )

        with self.assertRaises(DuplicatePaymentReference) as context:
            PaymentCreationService.create_payment(
                order=self.order,
                method=Payment.PAYMENT_METHOD_PIX,
                payment_reference="PAY-DUPLICATE-001",
            )

        self.assertEqual(
            str(context.exception),
            MSG_EXCEPTIONS_ERROR_PAYMENT_REFERENCE_ALREADY_EXISTS,
        )

    def test_validate_order_eligibility_accepts_pending_order(self):
        """Ensure eligibility validation accepts pending order and pending payment flow."""
        PaymentCreationService._validate_order_eligibility(order=self.order)

    def test_validate_order_has_totals_accepts_order_with_totals(self):
        """Ensure totals validation accepts order that has totals."""
        PaymentCreationService._validate_order_has_totals(order=self.order)

    def test_validate_order_has_no_payment_accepts_order_without_payment(self):
        """Ensure payment existence validation accepts order without payment."""
        PaymentCreationService._validate_order_has_no_payment(order=self.order)

    def test_validate_idempotency_key_accepts_unused_key(self):
        """Ensure idempotency validation accepts a fresh key."""
        PaymentCreationService._validate_idempotency_key(idempotency_key=uuid.uuid4())

    def test_validate_payment_reference_uniqueness_accepts_new_reference(self):
        """Ensure payment reference validation accepts an unused reference."""
        PaymentCreationService._validate_payment_reference_uniqueness(
            payment_reference="PAY-UNIQUE-001"
        )

    def test_get_order_amount_returns_grand_total(self):
        """Ensure helper returns order grand total as payment amount."""
        amount = PaymentCreationService._get_order_amount(order=self.order)

        self.assertEqual(amount, Decimal("100.00"))

    def test_get_order_currency_returns_order_currency(self):
        """Ensure helper returns order currency."""
        currency = PaymentCreationService._get_order_currency(order=self.order)

        self.assertEqual(currency, "USD")

    def test_generate_payment_reference_uses_expected_format(self):
        """Ensure generated payment reference uses expected prefix and format."""
        reference = PaymentCreationService._generate_payment_reference()

        self.assertTrue(reference.startswith("PAY-"))
        self.assertEqual(len(reference), 16)

    def test_validate_payment_consistency_raises_for_customer_mismatch(self):
        """Ensure consistency validation raises when payment customer differs from order customer."""
        payment = Payment.objects.create(
            order=self.order,
            customer=self.other_customer,
            payment_reference="PAY-MISMATCH-CUSTOMER",
            method=Payment.PAYMENT_METHOD_PIX,
            status=Payment.PAYMENT_STATUS_PENDING,
            amount=Decimal("100.00"),
        )

        with self.assertRaises(PaymentCustomerMismatch) as context:
            PaymentCreationService._validate_payment_consistency(
                payment=payment,
                order=self.order,
                expected_amount=Decimal("100.00"),
            )

        self.assertEqual(
            str(context.exception),
            MSG_EXCEPTIONS_ERROR_PAYMENT_CUSTOMER_DOES_NOT_MATCH,
        )

    def test_validate_payment_consistency_raises_for_amount_mismatch(self):
        """Ensure consistency validation raises when payment amount differs from expected."""
        payment = Payment.objects.create(
            order=self.order,
            customer=self.customer,
            payment_reference="PAY-MISMATCH-AMOUNT",
            method=Payment.PAYMENT_METHOD_PIX,
            status=Payment.PAYMENT_STATUS_PENDING,
            amount=Decimal("90.00"),
        )

        with self.assertRaises(PaymentAmountMismatch) as context:
            PaymentCreationService._validate_payment_consistency(
                payment=payment,
                order=self.order,
                expected_amount=Decimal("100.00"),
            )

        self.assertEqual(
            str(context.exception),
            MSG_EXCEPTIONS_ERROR_PAYMENT_AMOUNT_DOES_NOT_MATCH,
        )

    def test_validate_payment_consistency_accepts_matching_data(self):
        """Ensure consistency validation accepts matching payment and order data."""
        payment = Payment.objects.create(
            order=self.order,
            customer=self.customer,
            payment_reference="PAY-CONSISTENT-001",
            method=Payment.PAYMENT_METHOD_PIX,
            status=Payment.PAYMENT_STATUS_PENDING,
            amount=Decimal("100.00"),
        )

        PaymentCreationService._validate_payment_consistency(
            payment=payment,
            order=self.order,
            expected_amount=Decimal("100.00"),
        )