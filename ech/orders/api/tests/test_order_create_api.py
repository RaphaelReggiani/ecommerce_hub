from uuid import uuid4
from decimal import Decimal
from django.core.cache import cache

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ech.users.models import CustomUser
from ech.products.models import Product, ProductInventory
from ech.orders.models import (
    Order,
    OrderItem,
    OrderTotals,
    OrderAddress,
    OrderLifecycle,
)


class OrderCreateApiTestCase(APITestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse("orders-api:order-create")

        self.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.seller = CustomUser.objects.create_user(
            email="seller@test.com",
            password="StrongPassword123",
            user_name="Seller User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.product = Product.objects.create(
            name="Headset Pro",
            product_type=Product.HEADSET,
            brand="Logitech",
            sold_by=self.seller,
            description="Great headset",
            technical_information="Noise cancelling",
            price=Decimal("100.00"),
            discount_price=Decimal("80.00"),
            is_active=True,
        )

        self.inventory = ProductInventory.objects.create(
            product=self.product,
            quantity=10,
        )

        self.valid_payload = {
            "items": [
                {
                    "product_id": str(self.product.id),
                    "quantity": 2,
                }
            ],
            "address": {
                "full_name": "User Tester",
                "address_line": "Rua Teste, 123",
                "city": "Sao Paulo",
                "state": "SP",
                "country": "Brazil",
                "postal_code": "01234-567",
                "phone": "11999999999",
            },
        }

    def authenticate(self, user=None):
        self.client.force_authenticate(user=user or self.customer)

    def test_create_order_successfully(self):
        self.authenticate()

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(OrderTotals.objects.count(), 1)
        self.assertEqual(OrderAddress.objects.count(), 1)
        self.assertEqual(OrderLifecycle.objects.count(), 1)

        order = Order.objects.select_related(
            "totals",
            "address",
            "lifecycle",
        ).get()

        item = order.items.get()

        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.status, Order.ORDER_STATUS_PENDING)
        self.assertEqual(order.payment_status, Order.PAYMENT_STATUS_PENDING)
        self.assertEqual(order.shipping_status, Order.SHIPPING_STATUS_PENDING)
        self.assertEqual(order.currency, "USD")

        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.unit_price, Decimal("100.00"))
        self.assertEqual(item.discount_price, Decimal("80.00"))
        self.assertEqual(item.total_price, Decimal("160.00"))
        self.assertEqual(item.product_name_snapshot, self.product.name)
        self.assertEqual(item.brand_snapshot, self.product.brand)
        self.assertEqual(item.product_type_snapshot, self.product.product_type)

        self.assertEqual(order.totals.subtotal, Decimal("200.00"))
        self.assertEqual(order.totals.discount_total, Decimal("40.00"))
        self.assertEqual(order.totals.tax_total, Decimal("0.00"))
        self.assertEqual(order.totals.shipping_total, Decimal("0.00"))
        self.assertEqual(order.totals.grand_total, Decimal("160.00"))

        self.assertEqual(order.address.full_name, "User Tester")
        self.assertEqual(order.address.address_line, "Rua Teste, 123")
        self.assertEqual(order.address.city, "Sao Paulo")
        self.assertEqual(order.address.state, "SP")
        self.assertEqual(order.address.country, "Brazil")
        self.assertEqual(order.address.postal_code, "01234-567")
        self.assertEqual(order.address.phone, "11999999999")

        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 8)

        self.assertEqual(response.data["id"], str(order.id))
        self.assertEqual(response.data["status"], Order.ORDER_STATUS_PENDING)
        self.assertEqual(response.data["payment_status"], Order.PAYMENT_STATUS_PENDING)
        self.assertEqual(response.data["shipping_status"], Order.SHIPPING_STATUS_PENDING)
        self.assertEqual(response.data["customer"], self.customer.id)
        self.assertEqual(response.data["customer_name"], self.customer.user_name)
        self.assertEqual(response.data["customer_email"], self.customer.user_email)
        self.assertEqual(len(response.data["items"]), 1)
        self.assertEqual(response.data["totals"]["grand_total"], "160.00")

    def test_create_order_returns_unauthorized_for_unauthenticated_user(self):
        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )
        self.assertEqual(Order.objects.count(), 0)

    def test_create_order_fails_when_items_is_empty(self):
        self.authenticate()

        payload = {
            "items": [],
            "address": self.valid_payload["address"],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("items", response.data)
        self.assertEqual(Order.objects.count(), 0)

    def test_create_order_fails_when_product_is_inactive(self):
        self.authenticate()

        self.product.is_active = False
        self.product.save(update_fields=["is_active"])

        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("items", response.data)
        self.assertEqual(Order.objects.count(), 0)

    def test_create_order_fails_when_product_id_does_not_exist(self):
        self.authenticate()

        payload = {
            **self.valid_payload,
            "items": [
                {
                    "product_id": str(uuid4()),
                    "quantity": 1,
                }
            ],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("items", response.data)
        self.assertEqual(Order.objects.count(), 0)

    def test_create_order_fails_when_quantity_is_less_than_one(self):
        self.authenticate()

        payload = {
            **self.valid_payload,
            "items": [
                {
                    "product_id": str(self.product.id),
                    "quantity": 0,
                }
            ],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("items", response.data)
        self.assertEqual(Order.objects.count(), 0)

    def test_create_order_fails_when_inventory_is_insufficient(self):
        self.authenticate()

        payload = {
            **self.valid_payload,
            "items": [
                {
                    "product_id": str(self.product.id),
                    "quantity": 999,
                }
            ],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)
        self.assertEqual(OrderTotals.objects.count(), 0)
        self.assertEqual(OrderAddress.objects.count(), 0)
        self.assertEqual(OrderLifecycle.objects.count(), 0)

        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 10)

    def test_create_order_fails_when_address_is_missing(self):
        self.authenticate()

        payload = {
            "items": self.valid_payload["items"],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("address", response.data)
        self.assertEqual(Order.objects.count(), 0)

    def test_create_order_fails_when_address_required_field_is_missing(self):
        self.authenticate()

        payload = {
            "items": self.valid_payload["items"],
            "address": {
                "address_line": "Rua Teste, 123",
                "city": "Sao Paulo",
                "state": "SP",
                "country": "Brazil",
                "postal_code": "01234-567",
            },
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("address", response.data)
        self.assertEqual(Order.objects.count(), 0)

    def test_create_order_allows_blank_phone(self):
        self.authenticate()

        payload = {
            **self.valid_payload,
            "address": {
                **self.valid_payload["address"],
                "phone": "",
            },
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        order = Order.objects.get()
        self.assertEqual(order.address.phone, "")

    def test_create_order_returns_existing_order_when_idempotency_key_is_reused(self):
        self.authenticate()

        idempotency_key = str(uuid4())
        payload = {
            **self.valid_payload,
            "idempotency_key": idempotency_key,
        }

        first_response = self.client.post(self.url, payload, format="json")
        second_response = self.client.post(self.url, payload, format="json")

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(OrderTotals.objects.count(), 1)
        self.assertEqual(OrderAddress.objects.count(), 1)
        self.assertEqual(OrderLifecycle.objects.count(), 1)

        order = Order.objects.get()
        self.assertEqual(str(order.id), first_response.data["id"])
        self.assertEqual(str(order.id), second_response.data["id"])

        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 8)

    def test_create_order_supports_product_without_discount(self):
        self.authenticate()

        self.product.discount_price = None
        self.product.save(update_fields=["discount_price"])

        payload = {
            **self.valid_payload,
            "items": [
                {
                    "product_id": str(self.product.id),
                    "quantity": 3,
                }
            ],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        order = Order.objects.select_related("totals").get()
        item = order.items.get()

        self.assertEqual(item.discount_price, None)
        self.assertEqual(item.total_price, Decimal("300.00"))
        self.assertEqual(order.totals.subtotal, Decimal("300.00"))
        self.assertEqual(order.totals.discount_total, Decimal("0.00"))
        self.assertEqual(order.totals.grand_total, Decimal("300.00"))

        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 7)