from decimal import Decimal
from datetime import timedelta
from django.core.cache import cache

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from ech.users.models import CustomUser
from ech.orders.models import Order, OrderTotals


class OrderManagementListApiTestCase(APITestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse("orders-api:order-management-list")

        self.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.staff = CustomUser.objects.create_user(
            email="staff@company.com",
            password="StrongPassword123",
            user_name="Staff User",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            is_active=True,
            email_confirmed=True,
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def create_order(
        self,
        *,
        customer,
        status_value=Order.ORDER_STATUS_PENDING,
        payment_status=Order.PAYMENT_STATUS_PENDING,
        shipping_status=Order.SHIPPING_STATUS_PENDING,
        created_at=None,
    ):
        order = Order.objects.create(
            customer=customer,
            status=status_value,
            payment_status=payment_status,
            shipping_status=shipping_status,
        )

        if created_at:
            Order.objects.filter(id=order.id).update(created_at=created_at)
            order.refresh_from_db()

        OrderTotals.objects.create(
            order=order,
            subtotal=Decimal("100.00"),
            discount_total=Decimal("0.00"),
            tax_total=Decimal("0.00"),
            shipping_total=Decimal("0.00"),
            grand_total=Decimal("100.00"),
        )

        return order

    def test_management_list_requires_authentication(self):
        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_management_list_denied_for_non_staff_user(self):
        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_management_list_allowed_for_staff(self):
        self.authenticate(self.staff)

        self.create_order(customer=self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_management_list_returns_all_orders(self):
        self.authenticate(self.staff)

        self.create_order(customer=self.customer)
        self.create_order(customer=self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_management_list_is_ordered_by_created_at_desc(self):
        self.authenticate(self.staff)

        older = self.create_order(customer=self.customer)

        newer = self.create_order(customer=self.customer)

        response = self.client.get(self.url)

        results = response.data["results"]

        self.assertEqual(results[0]["id"], str(newer.id))
        self.assertEqual(results[1]["id"], str(older.id))

    def test_filter_by_status(self):
        self.authenticate(self.staff)

        self.create_order(customer=self.customer, status_value=Order.ORDER_STATUS_PENDING)
        self.create_order(customer=self.customer, status_value=Order.ORDER_STATUS_CONFIRMED)

        response = self.client.get(self.url, {"status": "confirmed"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["status"], "confirmed")

    def test_filter_by_payment_status(self):
        self.authenticate(self.staff)

        self.create_order(customer=self.customer, payment_status=Order.PAYMENT_STATUS_PENDING)
        self.create_order(customer=self.customer, payment_status=Order.PAYMENT_STATUS_CAPTURED)

        response = self.client.get(self.url, {"payment_status": "captured"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["payment_status"], "captured")

    def test_filter_by_shipping_status(self):
        self.authenticate(self.staff)

        self.create_order(customer=self.customer, shipping_status=Order.SHIPPING_STATUS_PENDING)
        self.create_order(customer=self.customer, shipping_status=Order.SHIPPING_STATUS_SHIPPED)

        response = self.client.get(self.url, {"shipping_status": "shipped"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["shipping_status"], "shipped")

    def test_filter_by_customer_email(self):
        self.authenticate(self.staff)

        self.create_order(customer=self.customer)

        other = CustomUser.objects.create_user(
            email="another@test.com",
            password="StrongPassword123",
            user_name="Another",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.create_order(customer=other)

        response = self.client.get(self.url, {"customer_email": "another"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertIn("another@test.com", response.data["results"][0]["customer_email"])

    def test_filter_by_customer_name(self):
        self.authenticate(self.staff)

        self.create_order(customer=self.customer)

        other = CustomUser.objects.create_user(
            email="name@test.com",
            password="StrongPassword123",
            user_name="John Doe",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.create_order(customer=other)

        response = self.client.get(self.url, {"customer_name": "john"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["customer_name"], "John Doe")

    def test_filter_by_created_date_range(self):
        self.authenticate(self.staff)

        now = timezone.now()

        old_order = self.create_order(
            customer=self.customer,
            created_at=now - timedelta(days=5),
        )

        new_order = self.create_order(
            customer=self.customer,
            created_at=now,
        )

        response = self.client.get(self.url, {
            "created_after": (now - timedelta(days=1)).isoformat()
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(new_order.id))

    def test_management_list_pagination(self):
        self.authenticate(self.staff)

        for _ in range(5):
            self.create_order(customer=self.customer)

        response = self.client.get(self.url, {"page_size": 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 5)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertIsNotNone(response.data["next"])