from datetime import timedelta
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from ech.orders.filters import OrderFilter
from ech.orders.models import Order


class BaseOrderFilterFactoryMixin:
    user_counter = 0

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


class OrderFilterTestCase(BaseOrderFilterFactoryMixin, TestCase):
    def test_filter_by_status(self):
        """Filter orders correctly by status."""
        matching_order = self.create_order(status=Order.ORDER_STATUS_PENDING)
        self.create_order(status=Order.ORDER_STATUS_CANCELLED)

        filtered_qs = OrderFilter(
            data={"status": Order.ORDER_STATUS_PENDING},
            queryset=Order.objects.all(),
        ).qs

        self.assertEqual(filtered_qs.count(), 1)
        self.assertIn(matching_order, filtered_qs)

    def test_filter_by_status_is_case_insensitive(self):
        """Filter orders by status using case-insensitive input."""
        matching_order = self.create_order(status=Order.ORDER_STATUS_PENDING)
        self.create_order(status=Order.ORDER_STATUS_CANCELLED)

        filtered_qs = OrderFilter(
            data={"status": "PENDING"},
            queryset=Order.objects.all(),
        ).qs

        self.assertEqual(filtered_qs.count(), 1)
        self.assertIn(matching_order, filtered_qs)

    def test_filter_by_payment_status(self):
        """Filter orders correctly by payment status."""
        matching_order = self.create_order(payment_status=Order.PAYMENT_STATUS_PENDING)
        self.create_order(payment_status=Order.PAYMENT_STATUS_CAPTURED)

        filtered_qs = OrderFilter(
            data={"payment_status": Order.PAYMENT_STATUS_PENDING},
            queryset=Order.objects.all(),
        ).qs

        self.assertEqual(filtered_qs.count(), 1)
        self.assertIn(matching_order, filtered_qs)

    def test_filter_by_payment_status_is_case_insensitive(self):
        """Filter orders by payment status using case-insensitive input."""
        matching_order = self.create_order(payment_status=Order.PAYMENT_STATUS_PENDING)
        self.create_order(payment_status=Order.PAYMENT_STATUS_FAILED)

        filtered_qs = OrderFilter(
            data={"payment_status": "PENDING"},
            queryset=Order.objects.all(),
        ).qs

        self.assertEqual(filtered_qs.count(), 1)
        self.assertIn(matching_order, filtered_qs)

    def test_filter_by_shipping_status(self):
        """Filter orders correctly by shipping status."""
        matching_order = self.create_order(shipping_status=Order.SHIPPING_STATUS_PENDING)
        self.create_order(shipping_status=Order.SHIPPING_STATUS_DELIVERED)

        filtered_qs = OrderFilter(
            data={"shipping_status": Order.SHIPPING_STATUS_PENDING},
            queryset=Order.objects.all(),
        ).qs

        self.assertEqual(filtered_qs.count(), 1)
        self.assertIn(matching_order, filtered_qs)

    def test_filter_by_shipping_status_is_case_insensitive(self):
        """Filter orders by shipping status using case-insensitive input."""
        matching_order = self.create_order(shipping_status=Order.SHIPPING_STATUS_PENDING)
        self.create_order(shipping_status=Order.SHIPPING_STATUS_SHIPPED)

        filtered_qs = OrderFilter(
            data={"shipping_status": "PENDING"},
            queryset=Order.objects.all(),
        ).qs

        self.assertEqual(filtered_qs.count(), 1)
        self.assertIn(matching_order, filtered_qs)

    def test_filter_by_customer_email_using_icontains(self):
        """Filter orders by partial customer email using icontains."""
        matching_customer = self.create_user(
            user_email="alpha.customer@test.com",
            user_name="Alpha Customer",
        )
        other_customer = self.create_user(
            user_email="beta.user@test.com",
            user_name="Beta User",
        )

        matching_order = self.create_order(customer=matching_customer)
        self.create_order(customer=other_customer)

        filtered_qs = OrderFilter(
            data={"customer_email": "customer@test"},
            queryset=Order.objects.all(),
        ).qs

        self.assertEqual(filtered_qs.count(), 1)
        self.assertIn(matching_order, filtered_qs)

    def test_filter_by_customer_email_is_case_insensitive(self):
        """Filter orders by customer email using case-insensitive matching."""
        matching_customer = self.create_user(
            user_email="mixed.case@test.com",
            user_name="Mixed Case",
        )
        other_customer = self.create_user(
            user_email="other.user@test.com",
            user_name="Other User",
        )

        matching_order = self.create_order(customer=matching_customer)
        self.create_order(customer=other_customer)

        filtered_qs = OrderFilter(
            data={"customer_email": "MIXED.CASE"},
            queryset=Order.objects.all(),
        ).qs

        self.assertEqual(filtered_qs.count(), 1)
        self.assertIn(matching_order, filtered_qs)

    def test_filter_by_customer_name_using_icontains(self):
        """Filter orders by partial customer name using icontains."""
        matching_customer = self.create_user(
            user_email="customer1@test.com",
            user_name="Example Customer",
        )
        other_customer = self.create_user(
            user_email="customer2@test.com",
            user_name="Another User",
        )

        matching_order = self.create_order(customer=matching_customer)
        self.create_order(customer=other_customer)

        filtered_qs = OrderFilter(
            data={"customer_name": "example"},
            queryset=Order.objects.all(),
        ).qs

        self.assertEqual(filtered_qs.count(), 1)
        self.assertIn(matching_order, filtered_qs)

    def test_filter_by_customer_name_is_case_insensitive(self):
        """Filter orders by customer name using case-insensitive matching."""
        matching_customer = self.create_user(
            user_email="customer3@test.com",
            user_name="Sample Buyer",
        )
        other_customer = self.create_user(
            user_email="customer4@test.com",
            user_name="Different Person",
        )

        matching_order = self.create_order(customer=matching_customer)
        self.create_order(customer=other_customer)

        filtered_qs = OrderFilter(
            data={"customer_name": "SAMPLE"},
            queryset=Order.objects.all(),
        ).qs

        self.assertEqual(filtered_qs.count(), 1)
        self.assertIn(matching_order, filtered_qs)

    def test_filter_by_created_after(self):
        """Filter orders created after the specified timestamp."""
        older_order = self.create_order()
        newer_order = self.create_order()

        threshold = older_order.created_at + timedelta(microseconds=1)

        filtered_qs = OrderFilter(
            data={"created_after": threshold.isoformat()},
            queryset=Order.objects.all(),
        ).qs

        self.assertNotIn(older_order, filtered_qs)
        self.assertIn(newer_order, filtered_qs)

    def test_filter_by_created_before(self):
        """Filter orders created before the specified timestamp."""
        older_order = self.create_order()
        newer_order = self.create_order()

        threshold = newer_order.created_at - timedelta(microseconds=1)

        filtered_qs = OrderFilter(
            data={"created_before": threshold.isoformat()},
            queryset=Order.objects.all(),
        ).qs

        self.assertIn(older_order, filtered_qs)
        self.assertNotIn(newer_order, filtered_qs)

    def test_filter_combines_multiple_fields(self):
        """Filter orders correctly when multiple filter fields are combined."""
        target_customer = self.create_user(
            user_email="target.customer@test.com",
            user_name="Target Customer",
        )
        other_customer = self.create_user(
            user_email="other.customer@test.com",
            user_name="Other Customer",
        )

        matching_order = self.create_order(
            customer=target_customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
        )

        self.create_order(
            customer=target_customer,
            status=Order.ORDER_STATUS_CANCELLED,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
        )

        self.create_order(
            customer=other_customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
        )

        filtered_qs = OrderFilter(
            data={
                "status": Order.ORDER_STATUS_PENDING,
                "customer_email": "target.customer",
                "customer_name": "target",
            },
            queryset=Order.objects.all(),
        ).qs

        self.assertEqual(filtered_qs.count(), 1)
        self.assertIn(matching_order, filtered_qs)

    def test_filter_returns_all_orders_when_no_data_is_provided(self):
        """Return all orders when no filter data is provided."""
        first_order = self.create_order()
        second_order = self.create_order()

        filtered_qs = OrderFilter(
            data={},
            queryset=Order.objects.all(),
        ).qs

        self.assertEqual(filtered_qs.count(), 2)
        self.assertIn(first_order, filtered_qs)
        self.assertIn(second_order, filtered_qs)

    def test_filter_meta_model_is_order(self):
        """Ensure OrderFilter meta model is Order."""
        self.assertEqual(OrderFilter._meta.model, Order)

    def test_filter_meta_fields_are_expected(self):
        """Ensure OrderFilter exposes the expected filter fields."""
        self.assertEqual(
            OrderFilter._meta.fields,
            [
                "status",
                "payment_status",
                "shipping_status",
                "customer_email",
                "customer_name",
                "created_after",
                "created_before",
            ],
        )