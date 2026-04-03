from decimal import Decimal
import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from ech.orders.exceptions import (
    EmptyOrderError,
    ProductNotAvailableError,
    InsufficientInventoryError,
    InvalidOrderAddressError,
)
from ech.orders.models import (
    Order,
    OrderItem,
    OrderTotals,
    OrderLifecycle,
    OrderEvent,
    OrderAddress,
)
from ech.orders.services.order_create_service import CreateOrderService
from ech.products.models import Product, ProductInventory


class BaseCreateOrderFactoryMixin:
    user_counter = 0
    product_counter = 0

    def create_user(self, **overrides):
        User = get_user_model()
        self.__class__.user_counter += 1
        idx = self.__class__.user_counter

        model_fields = {field.name: field for field in User._meta.fields}
        unique_suffix = uuid.uuid4().hex[:8]
        unique_email = f"user_{idx}_{unique_suffix}@test.com"

        data = {}

        if "email" in model_fields:
            data["email"] = unique_email

        if "user_email" in model_fields:
            data["user_email"] = unique_email

        if "username" in model_fields:
            data["username"] = f"user_{idx}_{unique_suffix}"

        if "user_name" in model_fields:
            data["user_name"] = f"Test User {idx}"

        if "first_name" in model_fields:
            data["first_name"] = "Test"

        if "last_name" in model_fields:
            data["last_name"] = f"User{idx}"

        if "is_active" in model_fields:
            data["is_active"] = True

        data.update(overrides)

        manager = User.objects

        if hasattr(manager, "create_user"):
            try:
                return manager.create_user(password="StrongPass123!", **data)
            except TypeError:
                pass
            except Exception:
                pass

        user = manager.create(**data)

        if hasattr(user, "set_password"):
            user.set_password("StrongPass123!")
            user.save(update_fields=["password"])

        return user

    def create_product(self, **overrides):
        self.__class__.product_counter += 1
        idx = self.__class__.product_counter

        data = {
            "name": f"Product {idx}",
            "product_type": Product.MOUSE,
            "brand": "Test Brand",
            "sold_by": self.create_user(),
            "description": "Test product description.",
            "technical_information": "Test technical information.",
            "price": Decimal("100.00"),
            "discount_price": Decimal("80.00"),
            "is_active": True,
        }
        data.update(overrides)
        return Product.objects.create(**data)

    def create_inventory(self, product, quantity=10):
        return ProductInventory.objects.create(
            product=product,
            quantity=quantity,
        )

    def build_address(self, **overrides):
        data = {
            "full_name": "Test Customer",
            "address_line": "123 Test Street",
            "city": "Test City",
            "state": "TS",
            "country": "Test Country",
            "postal_code": "00000-000",
            "phone": "+00 00000-0000",
        }
        data.update(overrides)
        return data


class CreateOrderServiceTestCase(BaseCreateOrderFactoryMixin, TestCase):
    def test_execute_raises_empty_order_error_when_items_is_empty(self):
        """Raise EmptyOrderError when attempting to create an order with no items."""
        customer = self.create_user()
        address = self.build_address()

        service = CreateOrderService(
            customer=customer,
            items=[],
            address=address,
        )

        with self.assertRaises(EmptyOrderError):
            service.execute()

        self.assertEqual(Order.objects.count(), 0)

    def test_execute_returns_existing_order_when_idempotency_key_already_exists(self):
        """Return the existing order when the idempotency key already exists."""
        customer = self.create_user()
        existing_order = Order.objects.create(
            customer=customer,
            idempotency_key=uuid.uuid4(),
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
        )

        product = self.create_product()
        self.create_inventory(product=product, quantity=10)

        service = CreateOrderService(
            customer=customer,
            items=[{"product_id": product.id, "quantity": 2}],
            address=self.build_address(),
            idempotency_key=existing_order.idempotency_key,
        )

        result = service.execute()

        self.assertEqual(result.id, existing_order.id)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 0)
        self.assertEqual(OrderTotals.objects.count(), 0)
        self.assertEqual(OrderLifecycle.objects.count(), 0)
        self.assertEqual(OrderEvent.objects.count(), 0)
        self.assertEqual(OrderAddress.objects.count(), 0)

    def test_execute_raises_product_not_available_error_when_product_selector_returns_none(self):
        """Raise ProductNotAvailableError when the product selector returns None."""
        
        customer = self.create_user()

        service = CreateOrderService(
            customer=customer,
            items=[{"product_id": uuid.uuid4(), "quantity": 1}],
            address=self.build_address(),
        )

        with patch(
            "ech.orders.services.order_create_service.get_active_product_by_id",
            return_value=None,
        ):
            with self.assertRaises(ProductNotAvailableError):
                service.execute()

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)

    def test_execute_raises_insufficient_inventory_error_when_inventory_does_not_exist(self):
        """Raise InsufficientInventoryError when product inventory does not exist."""
        customer = self.create_user()
        product = self.create_product()

        service = CreateOrderService(
            customer=customer,
            items=[{"product_id": product.id, "quantity": 1}],
            address=self.build_address(),
        )

        with self.assertRaises(InsufficientInventoryError):
            service.execute()

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)

    def test_execute_raises_insufficient_inventory_error_when_inventory_is_less_than_requested_quantity(self):
        """Raise InsufficientInventoryError when inventory quantity is insufficient."""
        customer = self.create_user()
        product = self.create_product()
        self.create_inventory(product=product, quantity=1)

        service = CreateOrderService(
            customer=customer,
            items=[{"product_id": product.id, "quantity": 2}],
            address=self.build_address(),
        )

        with self.assertRaises(InsufficientInventoryError):
            service.execute()

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)
        self.assertEqual(OrderTotals.objects.count(), 0)

    def test_execute_raises_invalid_order_address_error_when_address_is_none(self):
        """Raise InvalidOrderAddressError when the provided address is None."""
        customer = self.create_user()
        product = self.create_product()
        self.create_inventory(product=product, quantity=10)

        service = CreateOrderService(
            customer=customer,
            items=[{"product_id": product.id, "quantity": 1}],
            address=None,
        )

        with self.assertRaises(InvalidOrderAddressError):
            service.execute()

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)
        self.assertEqual(OrderTotals.objects.count(), 0)
        self.assertEqual(OrderLifecycle.objects.count(), 0)
        self.assertEqual(OrderEvent.objects.count(), 0)
        self.assertEqual(OrderAddress.objects.count(), 0)

    def test_execute_creates_order_with_expected_default_statuses(self):
        """Create order with default pending status, payment, and shipping states."""
        customer = self.create_user()
        product = self.create_product()
        self.create_inventory(product=product, quantity=10)

        service = CreateOrderService(
            customer=customer,
            items=[{"product_id": product.id, "quantity": 1}],
            address=self.build_address(),
        )

        order = service.execute()

        self.assertEqual(order.customer, customer)
        self.assertEqual(order.status, Order.ORDER_STATUS_PENDING)
        self.assertEqual(order.payment_status, Order.PAYMENT_STATUS_PENDING)
        self.assertEqual(order.shipping_status, Order.SHIPPING_STATUS_PENDING)
        self.assertIsNone(order.idempotency_key)

    def test_execute_creates_order_with_idempotency_key_when_provided(self):
        """Persist idempotency key when provided during order creation."""
        customer = self.create_user()
        product = self.create_product()
        self.create_inventory(product=product, quantity=10)
        idempotency_key = uuid.uuid4()

        service = CreateOrderService(
            customer=customer,
            items=[{"product_id": product.id, "quantity": 1}],
            address=self.build_address(),
            idempotency_key=idempotency_key,
        )

        order = service.execute()

        self.assertEqual(order.idempotency_key, idempotency_key)

    def test_execute_creates_order_item_with_product_snapshot_fields(self):
        """Create order item with correct product snapshot data."""
        customer = self.create_user()
        product = self.create_product(
            name="Pro Gaming Mouse",
            brand="HyperTech",
            product_type=Product.MOUSE,
            price=Decimal("150.00"),
            discount_price=Decimal("120.00"),
        )
        self.create_inventory(product=product, quantity=10)

        service = CreateOrderService(
            customer=customer,
            items=[{"product_id": product.id, "quantity": 2}],
            address=self.build_address(),
        )

        order = service.execute()
        item = order.items.first()

        self.assertEqual(item.product, product)
        self.assertEqual(item.product_name_snapshot, "Pro Gaming Mouse")
        self.assertEqual(item.brand_snapshot, "HyperTech")
        self.assertEqual(item.product_type_snapshot, Product.MOUSE)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.unit_price, Decimal("150.00"))
        self.assertEqual(item.discount_price, Decimal("120.00"))
        self.assertEqual(item.total_price, Decimal("240.00"))

    def test_execute_updates_inventory_after_order_creation(self):
        """Decrease product inventory after successful order creation."""
        customer = self.create_user()
        product = self.create_product()
        inventory = self.create_inventory(product=product, quantity=10)

        service = CreateOrderService(
            customer=customer,
            items=[{"product_id": product.id, "quantity": 3}],
            address=self.build_address(),
        )

        service.execute()

        inventory.refresh_from_db()
        self.assertEqual(inventory.quantity, 7)

    def test_execute_creates_totals_correctly_for_single_discounted_item(self):
        """Calculate totals correctly for a single discounted product."""
        customer = self.create_user()
        product = self.create_product(
            price=Decimal("100.00"),
            discount_price=Decimal("80.00"),
        )
        self.create_inventory(product=product, quantity=10)

        service = CreateOrderService(
            customer=customer,
            items=[{"product_id": product.id, "quantity": 2}],
            address=self.build_address(),
        )

        order = service.execute()
        totals = order.totals

        self.assertEqual(totals.subtotal, Decimal("200.00"))
        self.assertEqual(totals.discount_total, Decimal("40.00"))
        self.assertEqual(totals.tax_total, Decimal("0.00"))
        self.assertEqual(totals.shipping_total, Decimal("0.00"))
        self.assertEqual(totals.grand_total, Decimal("160.00"))

    def test_execute_creates_totals_correctly_when_product_has_no_discount(self):
        """Calculate totals correctly when product has no discount."""
        customer = self.create_user()
        product = self.create_product(
            price=Decimal("75.00"),
            discount_price=None,
        )
        self.create_inventory(product=product, quantity=10)

        service = CreateOrderService(
            customer=customer,
            items=[{"product_id": product.id, "quantity": 2}],
            address=self.build_address(),
        )

        order = service.execute()
        totals = order.totals
        item = order.items.first()

        self.assertEqual(item.unit_price, Decimal("75.00"))
        self.assertIsNone(item.discount_price)
        self.assertEqual(item.total_price, Decimal("150.00"))
        self.assertEqual(totals.subtotal, Decimal("150.00"))
        self.assertEqual(totals.discount_total, Decimal("0.00"))
        self.assertEqual(totals.grand_total, Decimal("150.00"))

    def test_execute_creates_totals_correctly_for_multiple_items(self):
        """Calculate totals correctly when order contains multiple items."""
        customer = self.create_user()

        product_1 = self.create_product(
            price=Decimal("100.00"),
            discount_price=Decimal("90.00"),
        )
        product_2 = self.create_product(
            price=Decimal("50.00"),
            discount_price=None,
        )

        self.create_inventory(product=product_1, quantity=10)
        self.create_inventory(product=product_2, quantity=10)

        service = CreateOrderService(
            customer=customer,
            items=[
                {"product_id": product_1.id, "quantity": 2},
                {"product_id": product_2.id, "quantity": 3},
            ],
            address=self.build_address(),
        )

        order = service.execute()
        totals = order.totals

        self.assertEqual(totals.subtotal, Decimal("350.00"))
        self.assertEqual(totals.discount_total, Decimal("20.00"))
        self.assertEqual(totals.tax_total, Decimal("0.00"))
        self.assertEqual(totals.shipping_total, Decimal("0.00"))
        self.assertEqual(totals.grand_total, Decimal("330.00"))

    def test_execute_creates_lifecycle_with_all_status_dates_as_none(self):
        """Create lifecycle record with all status timestamps initially None."""
        customer = self.create_user()
        product = self.create_product()
        self.create_inventory(product=product, quantity=10)

        service = CreateOrderService(
            customer=customer,
            items=[{"product_id": product.id, "quantity": 1}],
            address=self.build_address(),
        )

        order = service.execute()
        lifecycle = order.lifecycle

        self.assertIsInstance(lifecycle, OrderLifecycle)
        self.assertIsNone(lifecycle.confirmed_at)
        self.assertIsNone(lifecycle.processing_at)
        self.assertIsNone(lifecycle.shipped_at)
        self.assertIsNone(lifecycle.delivered_at)
        self.assertIsNone(lifecycle.cancelled_at)
        self.assertIsNone(lifecycle.refunded_at)

    def test_execute_registers_created_event(self):
        """Register a created event when the order is successfully created."""
        customer = self.create_user()
        product = self.create_product()
        self.create_inventory(product=product, quantity=10)

        service = CreateOrderService(
            customer=customer,
            items=[{"product_id": product.id, "quantity": 1}],
            address=self.build_address(),
        )

        order = service.execute()
        event = order.events.first()

        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, OrderEvent.TYPE_CREATED)
        self.assertEqual(event.performed_by, customer)
        self.assertIn("created_at", event.metadata)

    def test_execute_creates_address_with_phone_when_provided(self):
        """Create order address including phone when provided."""
        customer = self.create_user()
        product = self.create_product()
        self.create_inventory(product=product, quantity=10)

        address = self.build_address(phone="+11 99999-9999")

        service = CreateOrderService(
            customer=customer,
            items=[{"product_id": product.id, "quantity": 1}],
            address=address,
        )

        order = service.execute()
        order_address = order.address

        self.assertEqual(order_address.full_name, "Test Customer")
        self.assertEqual(order_address.address_line, "123 Test Street")
        self.assertEqual(order_address.city, "Test City")
        self.assertEqual(order_address.state, "TS")
        self.assertEqual(order_address.country, "Test Country")
        self.assertEqual(order_address.postal_code, "00000-000")
        self.assertEqual(order_address.phone, "+11 99999-9999")

    def test_execute_creates_address_with_empty_phone_when_not_provided(self):
        """Create order address with empty phone when phone is not provided."""
        customer = self.create_user()
        product = self.create_product()
        self.create_inventory(product=product, quantity=10)

        address = self.build_address()
        address.pop("phone")

        service = CreateOrderService(
            customer=customer,
            items=[{"product_id": product.id, "quantity": 1}],
            address=address,
        )

        order = service.execute()

        self.assertEqual(order.address.phone, "")

    def test_execute_creates_all_related_records_successfully(self):
        """Create all related order records successfully during order creation."""
        customer = self.create_user()
        product = self.create_product()
        self.create_inventory(product=product, quantity=10)

        service = CreateOrderService(
            customer=customer,
            items=[{"product_id": product.id, "quantity": 2}],
            address=self.build_address(),
        )

        order = service.execute()

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(OrderTotals.objects.count(), 1)
        self.assertEqual(OrderLifecycle.objects.count(), 1)
        self.assertEqual(OrderEvent.objects.count(), 1)
        self.assertEqual(OrderAddress.objects.count(), 1)
        self.assertEqual(order.items.count(), 1)

    def test_execute_rolls_back_everything_when_address_is_invalid(self):
        """Rollback entire transaction when address validation fails."""
        customer = self.create_user()
        product = self.create_product()
        self.create_inventory(product=product, quantity=10)

        service = CreateOrderService(
            customer=customer,
            items=[{"product_id": product.id, "quantity": 1}],
            address={},
        )

        with self.assertRaises(InvalidOrderAddressError):
            service.execute()

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)
        self.assertEqual(OrderTotals.objects.count(), 0)
        self.assertEqual(OrderLifecycle.objects.count(), 0)
        self.assertEqual(OrderEvent.objects.count(), 0)
        self.assertEqual(OrderAddress.objects.count(), 0)

    def test_execute_rolls_back_order_when_second_item_has_insufficient_inventory(self):
        """Rollback order creation when a later item fails inventory validation."""
        customer = self.create_user()

        product_1 = self.create_product(price=Decimal("100.00"), discount_price=Decimal("90.00"))
        product_2 = self.create_product(price=Decimal("50.00"), discount_price=Decimal("40.00"))

        inventory_1 = self.create_inventory(product=product_1, quantity=10)
        inventory_2 = self.create_inventory(product=product_2, quantity=1)

        service = CreateOrderService(
            customer=customer,
            items=[
                {"product_id": product_1.id, "quantity": 2},
                {"product_id": product_2.id, "quantity": 5},
            ],
            address=self.build_address(),
        )

        with self.assertRaises(InsufficientInventoryError):
            service.execute()

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)
        self.assertEqual(OrderTotals.objects.count(), 0)
        self.assertEqual(OrderLifecycle.objects.count(), 0)
        self.assertEqual(OrderEvent.objects.count(), 0)
        self.assertEqual(OrderAddress.objects.count(), 0)

        inventory_1.refresh_from_db()
        inventory_2.refresh_from_db()

        self.assertEqual(inventory_1.quantity, 10)
        self.assertEqual(inventory_2.quantity, 1)

    @patch("ech.orders.services.order_create_service.OrderLogService.log_order_creation_failed")
    def test_execute_logs_failure_when_items_is_empty(self, log_failed_mock):
        customer = self.create_user()
        address = self.build_address()

        service = CreateOrderService(
            customer=customer,
            items=[],
            address=address,
        )

        with self.assertRaises(EmptyOrderError):
            service.execute()

        log_failed_mock.assert_called_once_with(
            customer=customer,
            idempotency_key=None,
            reason="empty_order_items",
        )

    @patch("ech.orders.services.order_create_service.OrderLogService.log_idempotency_replay")
    def test_execute_logs_idempotency_replay_when_existing_order_is_returned(
        self,
        log_replay_mock,
    ):
        customer = self.create_user()
        existing_order = Order.objects.create(
            customer=customer,
            idempotency_key=uuid.uuid4(),
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
        )

        product = self.create_product()
        self.create_inventory(product=product, quantity=10)

        service = CreateOrderService(
            customer=customer,
            items=[{"product_id": product.id, "quantity": 2}],
            address=self.build_address(),
            idempotency_key=existing_order.idempotency_key,
        )

        result = service.execute()

        self.assertEqual(result.id, existing_order.id)

        log_replay_mock.assert_called_once_with(
            order=existing_order,
            idempotency_key=existing_order.idempotency_key,
            metadata={
                "replayed_by_customer_id": customer.id,
            },
        )

    @patch("ech.orders.services.order_create_service.OrderLogService.log_order_creation_failed")
    def test_execute_logs_failure_when_product_is_not_available(
        self,
        log_failed_mock,
    ):
        customer = self.create_user()

        service = CreateOrderService(
            customer=customer,
            items=[{"product_id": uuid.uuid4(), "quantity": 1}],
            address=self.build_address(),
        )

        with patch(
            "ech.orders.services.order_create_service.get_active_product_by_id",
            return_value=None,
        ):
            with self.assertRaises(ProductNotAvailableError):
                service.execute()

        log_failed_mock.assert_called_once()
        _, kwargs = log_failed_mock.call_args

        self.assertEqual(kwargs["customer"], customer)
        self.assertIsNone(kwargs["idempotency_key"])
        self.assertEqual(kwargs["reason"], "ProductNotAvailableError")
        self.assertEqual(kwargs["metadata"]["items_count"], 1)
        self.assertIn("error_message", kwargs["metadata"])

    @patch("ech.orders.services.order_create_service.OrderLogService.log_order_creation_failed")
    def test_execute_logs_failure_when_inventory_is_insufficient(
        self,
        log_failed_mock,
    ):
        customer = self.create_user()
        product = self.create_product()
        self.create_inventory(product=product, quantity=1)

        service = CreateOrderService(
            customer=customer,
            items=[{"product_id": product.id, "quantity": 2}],
            address=self.build_address(),
        )

        with self.assertRaises(InsufficientInventoryError):
            service.execute()

        log_failed_mock.assert_called_once()
        _, kwargs = log_failed_mock.call_args

        self.assertEqual(kwargs["customer"], customer)
        self.assertIsNone(kwargs["idempotency_key"])
        self.assertEqual(kwargs["reason"], "InsufficientInventoryError")
        self.assertEqual(kwargs["metadata"]["items_count"], 1)
        self.assertIn("error_message", kwargs["metadata"])

    @patch("ech.orders.services.order_create_service.OrderLogService.log_order_creation_failed")
    def test_execute_logs_failure_when_address_is_invalid(
        self,
        log_failed_mock,
    ):
        customer = self.create_user()
        product = self.create_product()
        self.create_inventory(product=product, quantity=10)

        service = CreateOrderService(
            customer=customer,
            items=[{"product_id": product.id, "quantity": 1}],
            address=None,
        )

        with self.assertRaises(InvalidOrderAddressError):
            service.execute()

        log_failed_mock.assert_called_once()
        _, kwargs = log_failed_mock.call_args

        self.assertEqual(kwargs["customer"], customer)
        self.assertIsNone(kwargs["idempotency_key"])
        self.assertEqual(kwargs["reason"], "InvalidOrderAddressError")
        self.assertEqual(kwargs["metadata"]["items_count"], 1)
        self.assertIn("error_message", kwargs["metadata"])

    @patch("ech.orders.services.order_create_service.OrderLogService.log_order_created")
    def test_execute_logs_order_created_on_success(self, log_created_mock):
        customer = self.create_user()
        product = self.create_product(
            price=Decimal("100.00"),
            discount_price=Decimal("80.00"),
        )
        self.create_inventory(product=product, quantity=10)

        service = CreateOrderService(
            customer=customer,
            items=[{"product_id": product.id, "quantity": 2}],
            address=self.build_address(),
        )

        order = service.execute()

        log_created_mock.assert_called_once()
        _, kwargs = log_created_mock.call_args

        self.assertEqual(kwargs["order"], order)
        self.assertEqual(kwargs["metadata"]["items_count"], 1)
        self.assertEqual(kwargs["metadata"]["subtotal"], Decimal("200.00"))
        self.assertEqual(kwargs["metadata"]["discount_total"], Decimal("40.00"))
        self.assertEqual(kwargs["metadata"]["grand_total"], Decimal("160.00"))