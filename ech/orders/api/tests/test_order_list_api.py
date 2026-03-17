from decimal import Decimal
from time import sleep
from django.core.cache import cache

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ech.users.models import CustomUser
from ech.orders.models import Order, OrderTotals


class OrderListApiTestCase(APITestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse("orders-api:order-list")

        self.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.other_customer = CustomUser.objects.create_user(
            email="othercustomer@test.com",
            password="StrongPassword123",
            user_name="Other Customer",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

    def authenticate(self, user=None):
        self.client.force_authenticate(user=user or self.customer)

    def create_order(
        self,
        *,
        customer,
        status_value=Order.ORDER_STATUS_PENDING,
        payment_status=Order.PAYMENT_STATUS_PENDING,
        shipping_status=Order.SHIPPING_STATUS_PENDING,
        currency="USD",
        subtotal="100.00",
        discount_total="0.00",
        tax_total="0.00",
        shipping_total="0.00",
        grand_total="100.00",
    ):
        order = Order.objects.create(
            customer=customer,
            status=status_value,
            payment_status=payment_status,
            shipping_status=shipping_status,
            currency=currency,
        )

        OrderTotals.objects.create(
            order=order,
            subtotal=Decimal(subtotal),
            discount_total=Decimal(discount_total),
            tax_total=Decimal(tax_total),
            shipping_total=Decimal(shipping_total),
            grand_total=Decimal(grand_total),
        )

        return order

    def test_list_orders_returns_only_authenticated_customer_orders(self):
        self.authenticate(self.customer)

        customer_order_1 = self.create_order(
            customer=self.customer,
            grand_total="150.00",
        )
        customer_order_2 = self.create_order(
            customer=self.customer,
            status_value=Order.ORDER_STATUS_CONFIRMED,
            payment_status=Order.PAYMENT_STATUS_AUTHORIZED,
            shipping_status=Order.SHIPPING_STATUS_PREPARING,
            grand_total="300.00",
        )
        self.create_order(
            customer=self.other_customer,
            grand_total="999.00",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)

        returned_ids = {item["id"] for item in response.data["results"]}

        self.assertIn(str(customer_order_1.id), returned_ids)
        self.assertIn(str(customer_order_2.id), returned_ids)

    def test_list_orders_returns_empty_results_when_customer_has_no_orders(self):
        self.authenticate(self.customer)

        self.create_order(customer=self.other_customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])

    def test_list_orders_requires_authentication(self):
        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_list_orders_is_ordered_by_created_at_descending(self):
        self.authenticate(self.customer)

        older_order = self.create_order(
            customer=self.customer,
            grand_total="100.00",
        )

        sleep(0.01)

        newer_order = self.create_order(
            customer=self.customer,
            grand_total="200.00",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        results = response.data["results"]

        self.assertEqual(results[0]["id"], str(newer_order.id))
        self.assertEqual(results[1]["id"], str(older_order.id))

    def test_list_orders_returns_expected_serializer_fields(self):
        self.authenticate(self.customer)

        order = self.create_order(
            customer=self.customer,
            status_value=Order.ORDER_STATUS_CONFIRMED,
            payment_status=Order.PAYMENT_STATUS_AUTHORIZED,
            shipping_status=Order.SHIPPING_STATUS_PREPARING,
            subtotal="250.00",
            discount_total="25.00",
            tax_total="0.00",
            shipping_total="10.00",
            grand_total="235.00",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        result = response.data["results"][0]

        self.assertEqual(result["id"], str(order.id))
        self.assertEqual(result["customer"], self.customer.id)
        self.assertEqual(result["customer_name"], self.customer.user_name)
        self.assertEqual(result["customer_email"], self.customer.user_email)
        self.assertEqual(result["status"], Order.ORDER_STATUS_CONFIRMED)
        self.assertEqual(result["payment_status"], Order.PAYMENT_STATUS_AUTHORIZED)
        self.assertEqual(result["shipping_status"], Order.SHIPPING_STATUS_PREPARING)
        self.assertEqual(result["currency"], "USD")

        self.assertIn("totals", result)
        self.assertEqual(result["totals"]["subtotal"], "250.00")
        self.assertEqual(result["totals"]["discount_total"], "25.00")
        self.assertEqual(result["totals"]["tax_total"], "0.00")
        self.assertEqual(result["totals"]["shipping_total"], "10.00")
        self.assertEqual(result["totals"]["grand_total"], "235.00")
        self.assertIn("updated_at", result["totals"])

        self.assertIn("created_at", result)
        self.assertIn("updated_at", result)

    def test_list_orders_supports_default_pagination_structure(self):
        self.authenticate(self.customer)

        for _ in range(3):
            self.create_order(customer=self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        self.assertIsNone(response.data["next"])
        self.assertIsNone(response.data["previous"])
        self.assertEqual(len(response.data["results"]), 3)

    def test_list_orders_supports_custom_page_size(self):
        self.authenticate(self.customer)

        for _ in range(5):
            self.create_order(customer=self.customer)

        response = self.client.get(self.url, {"page_size": 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 5)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertIsNotNone(response.data["next"])
        self.assertIsNone(response.data["previous"])

    def test_list_orders_respects_max_page_size(self):
        self.authenticate(self.customer)

        for _ in range(105):
            self.create_order(customer=self.customer)

        response = self.client.get(self.url, {"page_size": 999})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 105)
        self.assertEqual(len(response.data["results"]), 100)

    def test_list_orders_does_not_return_orders_from_other_customers_even_with_many_records(self):
        self.authenticate(self.customer)

        for _ in range(7):
            self.create_order(customer=self.customer)

        for _ in range(4):
            self.create_order(customer=self.other_customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 7)
        self.assertEqual(len(response.data["results"]), 7)

        for result in response.data["results"]:
            self.assertEqual(result["customer"], self.customer.id)
            self.assertEqual(result["customer_email"], self.customer.user_email)