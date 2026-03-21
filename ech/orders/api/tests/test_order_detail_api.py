from decimal import Decimal
from uuid import uuid4

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.cache import cache

from ech.users.models import CustomUser
from ech.products.models import Product
from ech.orders.models import (
    Order,
    OrderItem,
    OrderTotals,
    OrderAddress,
    OrderLifecycle,
    OrderEvent,
    OrderNote,
)


class OrderDetailApiTestCase(APITestCase):
    def setUp(self):
        cache.clear()
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

    def authenticate(self, user=None):
        self.client.force_authenticate(user=user or self.customer)

    def create_order_with_related_data(self, *, customer):
        order = Order.objects.create(
            customer=customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
            currency="USD",
        )

        OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name_snapshot=self.product.name,
            product_type_snapshot=self.product.product_type,
            brand_snapshot=self.product.brand,
            quantity=2,
            unit_price=Decimal("100.00"),
            discount_price=Decimal("80.00"),
            total_price=Decimal("160.00"),
        )

        OrderTotals.objects.create(
            order=order,
            subtotal=Decimal("200.00"),
            discount_total=Decimal("40.00"),
            tax_total=Decimal("0.00"),
            shipping_total=Decimal("0.00"),
            grand_total=Decimal("160.00"),
        )

        OrderAddress.objects.create(
            order=order,
            full_name="User Tester",
            address_line="Rua Teste, 123",
            city="Sao Paulo",
            state="SP",
            country="Brazil",
            postal_code="01234-567",
            phone="11999999999",
        )

        OrderLifecycle.objects.create(
            order=order,
            confirmed_at=None,
            processing_at=None,
            shipped_at=None,
            delivered_at=None,
            cancelled_at=None,
            refunded_at=None,
        )

        OrderEvent.objects.create(
            order=order,
            event_type=OrderEvent.TYPE_CREATED,
            performed_by=customer,
            metadata={"source": "test"},
        )

        OrderNote.objects.create(
            order=order,
            author=customer,
            message="Customer note",
            is_internal=False,
        )

        return order

    def test_order_detail_returns_order_for_owner(self):
        """Return order detail when requested by the order owner."""
        self.authenticate(self.customer)

        order = self.create_order_with_related_data(customer=self.customer)
        url = reverse("orders-api:order-detail", kwargs={"order_id": order.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(order.id))
        self.assertEqual(str(response.data["customer"]), str(self.customer.id))
        self.assertEqual(response.data["customer_name"], self.customer.user_name)
        self.assertEqual(response.data["customer_email"], self.customer.user_email)
        self.assertEqual(response.data["status"], Order.ORDER_STATUS_PENDING)
        self.assertEqual(response.data["payment_status"], Order.PAYMENT_STATUS_PENDING)
        self.assertEqual(response.data["shipping_status"], Order.SHIPPING_STATUS_PENDING)
        self.assertEqual(response.data["currency"], "USD")

    def test_order_detail_returns_nested_related_data(self):
        """Return nested related resources for order detail endpoint."""
        self.authenticate(self.customer)

        order = self.create_order_with_related_data(customer=self.customer)
        url = reverse("orders-api:order-detail", kwargs={"order_id": order.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("items", response.data)
        self.assertEqual(len(response.data["items"]), 1)

        item = response.data["items"][0]
        self.assertEqual(str(item["product"]), str(self.product.id))
        self.assertEqual(item["product_name_snapshot"], self.product.name)
        self.assertEqual(item["product_type_snapshot"], self.product.product_type)
        self.assertEqual(item["brand_snapshot"], self.product.brand)
        self.assertEqual(item["quantity"], 2)
        self.assertEqual(item["unit_price"], "100.00")
        self.assertEqual(item["discount_price"], "80.00")
        self.assertEqual(item["total_price"], "160.00")

        self.assertIn("totals", response.data)
        self.assertEqual(response.data["totals"]["subtotal"], "200.00")
        self.assertEqual(response.data["totals"]["discount_total"], "40.00")
        self.assertEqual(response.data["totals"]["tax_total"], "0.00")
        self.assertEqual(response.data["totals"]["shipping_total"], "0.00")
        self.assertEqual(response.data["totals"]["grand_total"], "160.00")

        self.assertIn("address", response.data)
        self.assertEqual(response.data["address"]["full_name"], "User Tester")
        self.assertEqual(response.data["address"]["address_line"], "Rua Teste, 123")
        self.assertEqual(response.data["address"]["city"], "Sao Paulo")
        self.assertEqual(response.data["address"]["state"], "SP")
        self.assertEqual(response.data["address"]["country"], "Brazil")
        self.assertEqual(response.data["address"]["postal_code"], "01234-567")
        self.assertEqual(response.data["address"]["phone"], "11999999999")

        self.assertIn("events", response.data)
        self.assertEqual(len(response.data["events"]), 1)

        event = response.data["events"][0]
        self.assertEqual(event["event_type"], OrderEvent.TYPE_CREATED)
        self.assertEqual(str(event["performed_by"]), str(self.customer.id))
        self.assertEqual(event["performed_by_name"], self.customer.user_name)
        self.assertEqual(event["performed_by_email"], self.customer.user_email)
        self.assertEqual(event["metadata"], {"source": "test"})

        self.assertIn("notes", response.data)
        self.assertEqual(len(response.data["notes"]), 1)

        note = response.data["notes"][0]
        self.assertEqual(str(note["author"]), str(self.customer.id))
        self.assertEqual(note["author_name"], self.customer.user_name)
        self.assertEqual(note["author_email"], self.customer.user_email)
        self.assertEqual(note["message"], "Customer note")
        self.assertFalse(note["is_internal"])

    def test_order_detail_denies_access_to_non_owner_without_management_role(self):
        """Deny access when user is not the order owner."""
        self.authenticate(self.other_customer)

        order = self.create_order_with_related_data(customer=self.customer)
        url = reverse("orders-api:order-detail", kwargs={"order_id": order.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_detail_requires_authentication(self):
        """Require authentication to access order detail endpoint."""
        order = self.create_order_with_related_data(customer=self.customer)
        url = reverse("orders-api:order-detail", kwargs={"order_id": order.id})

        response = self.client.get(url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_order_detail_returns_404_when_order_does_not_exist(self):
        """Return 404 when requested order does not exist."""
        self.authenticate(self.customer)

        url = reverse("orders-api:order-detail", kwargs={"order_id": uuid4()})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    def test_order_detail_returns_correct_order_when_customer_has_multiple_orders(self):
        """Return correct order when customer has multiple orders."""
        self.authenticate(self.customer)

        other_order = self.create_order_with_related_data(customer=self.customer)
        target_order = self.create_order_with_related_data(customer=self.customer)

        url = reverse("orders-api:order-detail", kwargs={"order_id": target_order.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(target_order.id))
        self.assertNotEqual(response.data["id"], str(other_order.id))

    def test_order_detail_returns_created_and_updated_fields(self):
        """Include created and updated timestamps in order detail response."""
        self.authenticate(self.customer)

        order = self.create_order_with_related_data(customer=self.customer)
        url = reverse("orders-api:order-detail", kwargs={"order_id": order.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

        self.assertIn("created_at", response.data["items"][0])
        self.assertIn("updated_at", response.data["totals"])
        self.assertIn("created_at", response.data["address"])
        self.assertIn("created_at", response.data["events"][0])
        self.assertIn("created_at", response.data["notes"][0])

    def test_order_detail_returns_partially_refunded_payment_status(self):
        """Return partially refunded payment status correctly."""
        self.authenticate(self.customer)

        order = Order.objects.create(
            customer=self.customer,
            status=Order.ORDER_STATUS_DELIVERED,
            payment_status=Order.PAYMENT_STATUS_PARTIALLY_REFUNDED,
            shipping_status=Order.SHIPPING_STATUS_DELIVERED,
            currency="USD",
        )

        OrderTotals.objects.create(
            order=order,
            subtotal=Decimal("200.00"),
            discount_total=Decimal("0.00"),
            tax_total=Decimal("0.00"),
            shipping_total=Decimal("0.00"),
            grand_total=Decimal("200.00"),
        )

        OrderAddress.objects.create(
            order=order,
            full_name="User Tester",
            address_line="Rua Teste, 123",
            city="Sao Paulo",
            state="SP",
            country="Brazil",
            postal_code="01234-567",
            phone="11999999999",
        )

        OrderLifecycle.objects.create(order=order)

        url = reverse("orders-api:order-detail", kwargs={"order_id": order.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["payment_status"],
            Order.PAYMENT_STATUS_PARTIALLY_REFUNDED,
        )