from decimal import Decimal
import uuid

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from ech.orders.models import (
    Order,
    OrderItem,
    OrderTotals,
    OrderAddress,
    OrderLifecycle,
    OrderEvent,
    OrderNote,
)
from ech.products.models import Product


class BaseModelFactoryMixin:
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
            data["user_name"] = f"User {idx}"

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
            "brand": "HyperBrand",
            "sold_by": self.create_user(),
            "description": "High performance gaming mouse.",
            "technical_information": "RGB, 12000 DPI, USB connection.",
            "price": Decimal("100.00"),
            "discount_price": Decimal("90.00"),
            "is_active": True,
        }
        data.update(overrides)
        return Product.objects.create(**data)

    def create_order(self, **overrides):
        data = {
            "customer": self.create_user(),
            "status": Order.ORDER_STATUS_PENDING,
            "payment_status": Order.PAYMENT_STATUS_PENDING,
            "shipping_status": Order.SHIPPING_STATUS_PENDING,
            "currency": "USD",
        }
        data.update(overrides)
        return Order.objects.create(**data)

    def create_order_item(self, **overrides):
        order = overrides.pop("order", self.create_order())
        product = overrides.pop("product", self.create_product())

        data = {
            "order": order,
            "product": product,
            "product_name_snapshot": "Gaming Mouse",
            "product_type_snapshot": Product.MOUSE,
            "brand_snapshot": "HyperBrand",
            "quantity": 2,
            "unit_price": Decimal("50.00"),
            "discount_price": Decimal("5.00"),
            "total_price": Decimal("95.00"),
        }
        data.update(overrides)
        return OrderItem.objects.create(**data)

    def create_order_totals(self, **overrides):
        order = overrides.pop("order", self.create_order())
        data = {
            "order": order,
            "subtotal": Decimal("100.00"),
            "discount_total": Decimal("10.00"),
            "tax_total": Decimal("5.00"),
            "shipping_total": Decimal("15.00"),
            "grand_total": Decimal("110.00"),
        }
        data.update(overrides)
        return OrderTotals.objects.create(**data)

    def create_order_address(self, **overrides):
        order = overrides.pop("order", self.create_order())
        data = {
            "order": order,
            "full_name": "User Tester",
            "address_line": "123 Main Street",
            "city": "Sao Paulo",
            "state": "SP",
            "country": "Brazil",
            "postal_code": "01234-567",
            "phone": "+55 11 99999-9999",
        }
        data.update(overrides)
        return OrderAddress.objects.create(**data)

    def create_order_lifecycle(self, **overrides):
        order = overrides.pop("order", self.create_order())
        data = {"order": order}
        data.update(overrides)
        return OrderLifecycle.objects.create(**data)

    def create_order_event(self, **overrides):
        order = overrides.pop("order", self.create_order())
        performed_by = overrides.pop("performed_by", self.create_user())
        data = {
            "order": order,
            "event_type": OrderEvent.TYPE_CREATED,
            "performed_by": performed_by,
            "metadata": {"source": "test"},
        }
        data.update(overrides)
        return OrderEvent.objects.create(**data)

    def create_order_note(self, **overrides):
        order = overrides.pop("order", self.create_order())
        author = overrides.pop("author", self.create_user())
        data = {
            "order": order,
            "author": author,
            "message": "Customer requested address confirmation.",
            "is_internal": False,
        }
        data.update(overrides)
        return OrderNote.objects.create(**data)


class OrderModelTestCase(BaseModelFactoryMixin, TestCase):
    def test_order_creation_success(self):
        order = self.create_order()

        self.assertIsInstance(order.id, uuid.UUID)
        self.assertEqual(order.status, Order.ORDER_STATUS_PENDING)
        self.assertEqual(order.payment_status, Order.PAYMENT_STATUS_PENDING)
        self.assertEqual(order.shipping_status, Order.SHIPPING_STATUS_PENDING)
        self.assertEqual(order.currency, "USD")
        self.assertIsNotNone(order.created_at)
        self.assertIsNotNone(order.updated_at)

    def test_order_str_returns_expected_value(self):
        order = self.create_order()
        self.assertEqual(str(order), f"Order {order.id}")

    def test_order_default_ordering_is_created_at_desc(self):
        older = self.create_order()
        newer = self.create_order()

        orders = list(Order.objects.all())
        self.assertEqual(orders[0], newer)
        self.assertEqual(orders[1], older)

    def test_order_idempotency_key_accepts_null(self):
        order = self.create_order(idempotency_key=None)
        self.assertIsNone(order.idempotency_key)

    def test_order_idempotency_key_must_be_unique_when_provided(self):
        idem_key = uuid.uuid4()
        self.create_order(idempotency_key=idem_key)

        with self.assertRaises(IntegrityError):
            self.create_order(idempotency_key=idem_key)

    def test_order_status_choices_contain_expected_values(self):
        values = {choice[0] for choice in Order.ORDER_STATUS_CHOICES}

        self.assertSetEqual(
            values,
            {
                Order.ORDER_STATUS_PENDING,
                Order.ORDER_STATUS_CONFIRMED,
                Order.ORDER_STATUS_PROCESSING,
                Order.ORDER_STATUS_SHIPPED,
                Order.ORDER_STATUS_DELIVERED,
                Order.ORDER_STATUS_CANCELLED,
                Order.ORDER_STATUS_REFUNDED,
            },
        )

    def test_order_payment_status_choices_contain_expected_values(self):
        values = {choice[0] for choice in Order.PAYMENT_STATUS_CHOICES}

        self.assertSetEqual(
            values,
            {
                Order.PAYMENT_STATUS_PENDING,
                Order.PAYMENT_STATUS_PROCESSING,
                Order.PAYMENT_STATUS_AUTHORIZED,
                Order.PAYMENT_STATUS_CAPTURED,
                Order.PAYMENT_STATUS_FAILED,
                Order.PAYMENT_STATUS_CANCELLED,
                Order.PAYMENT_STATUS_PARTIALLY_REFUNDED,
                Order.PAYMENT_STATUS_REFUNDED,
            },
        )

    def test_order_shipping_status_choices_contain_expected_values(self):
        values = {choice[0] for choice in Order.SHIPPING_STATUS_CHOICES}

        self.assertSetEqual(
            values,
            {
                Order.SHIPPING_STATUS_PENDING,
                Order.SHIPPING_STATUS_PREPARING,
                Order.SHIPPING_STATUS_SHIPPED,
                Order.SHIPPING_STATUS_IN_TRANSIT,
                Order.SHIPPING_STATUS_DELIVERED,
            },
        )

    def test_order_meta_ordering(self):
        self.assertEqual(Order._meta.ordering, ["-created_at"])

    def test_order_has_expected_indexes(self):
        index_names = {index.name for index in Order._meta.indexes}
        self.assertIn("order_customer_created_idx", index_names)
        self.assertIn("order_status_idx", index_names)

    def test_order_creation_accepts_processing_payment_status(self):
        order = self.create_order(
            payment_status=Order.PAYMENT_STATUS_PROCESSING
        )

        self.assertEqual(
            order.payment_status,
            Order.PAYMENT_STATUS_PROCESSING,
        )

    def test_order_creation_accepts_cancelled_payment_status(self):
        order = self.create_order(
            payment_status=Order.PAYMENT_STATUS_CANCELLED
        )

        self.assertEqual(
            order.payment_status,
            Order.PAYMENT_STATUS_CANCELLED,
        )

    def test_order_creation_accepts_partially_refunded_payment_status(self):
        order = self.create_order(
            payment_status=Order.PAYMENT_STATUS_PARTIALLY_REFUNDED
        )

        self.assertEqual(
            order.payment_status,
            Order.PAYMENT_STATUS_PARTIALLY_REFUNDED,
        )


class OrderItemModelTestCase(BaseModelFactoryMixin, TestCase):
    def test_order_item_creation_success(self):
        item = self.create_order_item()

        self.assertIsInstance(item.id, uuid.UUID)
        self.assertEqual(item.product_name_snapshot, "Gaming Mouse")
        self.assertEqual(item.product_type_snapshot, Product.MOUSE)
        self.assertEqual(item.brand_snapshot, "HyperBrand")
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.unit_price, Decimal("50.00"))
        self.assertEqual(item.discount_price, Decimal("5.00"))
        self.assertEqual(item.total_price, Decimal("95.00"))
        self.assertIsNotNone(item.created_at)

    def test_order_item_str_returns_expected_value(self):
        item = self.create_order_item(
            product_name_snapshot="Mechanical Keyboard",
            quantity=3,
        )
        self.assertEqual(str(item), "Mechanical Keyboard x3")

    def test_order_item_discount_price_can_be_null(self):
        item = self.create_order_item(discount_price=None)
        self.assertIsNone(item.discount_price)

    def test_order_item_belongs_to_order(self):
        order = self.create_order()
        item = self.create_order_item(order=order)

        self.assertEqual(item.order, order)
        self.assertIn(item, order.items.all())

    def test_order_item_has_expected_indexes(self):
        index_names = {index.name for index in OrderItem._meta.indexes}
        self.assertIn("orderitem_order_idx", index_names)


class OrderTotalsModelTestCase(BaseModelFactoryMixin, TestCase):
    def test_order_totals_creation_success(self):
        totals = self.create_order_totals()

        self.assertEqual(totals.subtotal, Decimal("100.00"))
        self.assertEqual(totals.discount_total, Decimal("10.00"))
        self.assertEqual(totals.tax_total, Decimal("5.00"))
        self.assertEqual(totals.shipping_total, Decimal("15.00"))
        self.assertEqual(totals.grand_total, Decimal("110.00"))
        self.assertIsNotNone(totals.updated_at)

    def test_order_totals_str_returns_expected_value(self):
        totals = self.create_order_totals()
        self.assertEqual(str(totals), f"Totals for Order {totals.order_id}")

    def test_order_totals_is_one_to_one_with_order(self):
        order = self.create_order()
        self.create_order_totals(order=order)

        with self.assertRaises(IntegrityError):
            self.create_order_totals(order=order)

    def test_order_totals_defaults_are_zero_for_discount_tax_shipping(self):
        order = self.create_order()
        totals = OrderTotals.objects.create(
            order=order,
            subtotal=Decimal("100.00"),
            grand_total=Decimal("100.00"),
        )

        self.assertEqual(totals.discount_total, Decimal("0"))
        self.assertEqual(totals.tax_total, Decimal("0"))
        self.assertEqual(totals.shipping_total, Decimal("0"))


class OrderAddressModelTestCase(BaseModelFactoryMixin, TestCase):
    def test_order_address_creation_success(self):
        address = self.create_order_address()

        self.assertEqual(address.full_name, "User Tester")
        self.assertEqual(address.address_line, "123 Main Street")
        self.assertEqual(address.city, "Sao Paulo")
        self.assertEqual(address.state, "SP")
        self.assertEqual(address.country, "Brazil")
        self.assertEqual(address.postal_code, "01234-567")
        self.assertEqual(address.phone, "+55 11 99999-9999")
        self.assertIsNotNone(address.created_at)

    def test_order_address_str_returns_expected_value(self):
        address = self.create_order_address(full_name="John Doe", city="Campinas")
        self.assertEqual(str(address), "John Doe - Campinas")

    def test_order_address_phone_can_be_blank(self):
        address = self.create_order_address(phone="")
        self.assertEqual(address.phone, "")

    def test_order_address_is_one_to_one_with_order(self):
        order = self.create_order()
        self.create_order_address(order=order)

        with self.assertRaises(IntegrityError):
            self.create_order_address(order=order)


class OrderLifecycleModelTestCase(BaseModelFactoryMixin, TestCase):
    def test_order_lifecycle_creation_success(self):
        lifecycle = self.create_order_lifecycle()

        self.assertIsNone(lifecycle.confirmed_at)
        self.assertIsNone(lifecycle.processing_at)
        self.assertIsNone(lifecycle.shipped_at)
        self.assertIsNone(lifecycle.delivered_at)
        self.assertIsNone(lifecycle.cancelled_at)
        self.assertIsNone(lifecycle.refunded_at)
        self.assertIsNotNone(lifecycle.created_at)
        self.assertIsNotNone(lifecycle.updated_at)

    def test_order_lifecycle_str_returns_expected_value(self):
        lifecycle = self.create_order_lifecycle()
        self.assertEqual(str(lifecycle), f"Lifecycle for Order {lifecycle.order_id}")

    def test_order_lifecycle_is_one_to_one_with_order(self):
        order = self.create_order()
        self.create_order_lifecycle(order=order)

        with self.assertRaises(IntegrityError):
            self.create_order_lifecycle(order=order)


class OrderEventModelTestCase(BaseModelFactoryMixin, TestCase):
    def test_order_event_creation_success(self):
        event = self.create_order_event()

        self.assertIsInstance(event.id, uuid.UUID)
        self.assertEqual(event.event_type, OrderEvent.TYPE_CREATED)
        self.assertIsNotNone(event.performed_by)
        self.assertEqual(event.metadata, {"source": "test"})
        self.assertIsNotNone(event.created_at)

    def test_order_event_str_returns_expected_value(self):
        event = self.create_order_event(event_type=OrderEvent.TYPE_CONFIRMED)
        self.assertEqual(str(event), f"{event.event_type} - {event.order.id}")

    def test_order_event_ordering_is_created_at_desc(self):
        older = self.create_order_event()
        newer = self.create_order_event()

        events = list(OrderEvent.objects.all())
        self.assertEqual(events[0], newer)
        self.assertEqual(events[1], older)

    def test_order_event_performed_by_can_be_null(self):
        event = self.create_order_event(performed_by=None)
        self.assertIsNone(event.performed_by)

    def test_order_event_metadata_can_be_null(self):
        event = self.create_order_event(metadata=None)
        self.assertIsNone(event.metadata)

    def test_order_event_type_constants_are_defined(self):
        self.assertEqual(OrderEvent.TYPE_CREATED, "order_created")
        self.assertEqual(OrderEvent.TYPE_CONFIRMED, "order_confirmed")
        self.assertEqual(OrderEvent.TYPE_PROCESSING_STARTED, "order_processing_started")
        self.assertEqual(OrderEvent.TYPE_SHIPPED, "order_shipped")
        self.assertEqual(OrderEvent.TYPE_DELIVERED, "order_delivered")
        self.assertEqual(OrderEvent.TYPE_CANCELLED, "order_cancelled")
        self.assertEqual(OrderEvent.TYPE_REFUNDED, "order_refunded")


class OrderNoteModelTestCase(BaseModelFactoryMixin, TestCase):
    def test_order_note_creation_success(self):
        note = self.create_order_note()

        self.assertEqual(note.message, "Customer requested address confirmation.")
        self.assertFalse(note.is_internal)
        self.assertIsNotNone(note.author)
        self.assertIsNotNone(note.created_at)

    def test_order_note_str_returns_expected_value(self):
        note = self.create_order_note()
        self.assertEqual(str(note), f"Note on {note.order_id}")

    def test_order_note_author_can_be_null(self):
        note = self.create_order_note(author=None)
        self.assertIsNone(note.author)

    def test_order_note_default_ordering_is_created_at_asc(self):
        older = self.create_order_note(message="First note")
        newer = self.create_order_note(message="Second note")

        notes = list(OrderNote.objects.all())
        self.assertEqual(notes[0], older)
        self.assertEqual(notes[1], newer)

    def test_order_note_meta_ordering(self):
        self.assertEqual(OrderNote._meta.ordering, ["created_at"])

    