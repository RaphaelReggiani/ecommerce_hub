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


class OrderManagementDetailApiTestCase(APITestCase):
    def setUp(self):
        cache.clear()
        self.url_name = "orders-api:order-management-detail"

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
            user_name="Staff",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            is_active=True,
            email_confirmed=True,
        )

        self.product = Product.objects.create(
            name="Keyboard Pro",
            product_type=Product.KEYBOARD,
            brand="Logitech",
            sold_by=self.customer,
            description="Keyboard",
            technical_information="Info",
            price=Decimal("150.00"),
            discount_price=Decimal("120.00"),
            is_active=True,
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def create_order_with_full_data(self, *, customer):
        order = Order.objects.create(
            customer=customer,
            status=Order.ORDER_STATUS_CONFIRMED,
            payment_status=Order.PAYMENT_STATUS_CAPTURED,
            shipping_status=Order.SHIPPING_STATUS_PREPARING,
            currency="USD",
        )

        OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name_snapshot=self.product.name,
            product_type_snapshot=self.product.product_type,
            brand_snapshot=self.product.brand,
            quantity=2,
            unit_price=Decimal("150.00"),
            discount_price=Decimal("120.00"),
            total_price=Decimal("240.00"),
        )

        OrderTotals.objects.create(
            order=order,
            subtotal=Decimal("300.00"),
            discount_total=Decimal("60.00"),
            tax_total=Decimal("0.00"),
            shipping_total=Decimal("0.00"),
            grand_total=Decimal("240.00"),
        )

        OrderAddress.objects.create(
            order=order,
            full_name="Test User",
            address_line="Street",
            city="City",
            state="State",
            country="Country",
            postal_code="00000",
            phone="123",
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
            message="Test note",
            is_internal=False,
        )

        return order

    # =========================
    # AUTH / PERMISSION
    # =========================

    def test_management_detail_requires_authentication(self):
        order = self.create_order_with_full_data(customer=self.customer)

        url = reverse(self.url_name, kwargs={"order_id": order.id})

        response = self.client.get(url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_management_detail_denied_for_non_staff(self):
        self.authenticate(self.customer)

        order = self.create_order_with_full_data(customer=self.customer)

        url = reverse(self.url_name, kwargs={"order_id": order.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_management_detail_allowed_for_staff(self):
        self.authenticate(self.staff)

        order = self.create_order_with_full_data(customer=self.customer)

        url = reverse(self.url_name, kwargs={"order_id": order.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # =========================
    # CORE BEHAVIOR
    # =========================

    def test_management_detail_returns_full_order_data(self):
        self.authenticate(self.staff)

        order = self.create_order_with_full_data(customer=self.customer)

        url = reverse(self.url_name, kwargs={"order_id": order.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data

        self.assertEqual(data["id"], str(order.id))
        self.assertEqual(str(data["customer"]), str(self.customer.id))
        self.assertEqual(data["customer_name"], self.customer.user_name)
        self.assertEqual(data["customer_email"], self.customer.user_email)

        self.assertEqual(data["status"], Order.ORDER_STATUS_CONFIRMED)
        self.assertEqual(data["payment_status"], Order.PAYMENT_STATUS_CAPTURED)
        self.assertEqual(data["shipping_status"], Order.SHIPPING_STATUS_PREPARING)

        self.assertEqual(len(data["items"]), 1)
        item = data["items"][0]

        self.assertEqual(str(item["product"]), str(self.product.id))
        self.assertEqual(item["quantity"], 2)
        self.assertEqual(item["unit_price"], "150.00")
        self.assertEqual(item["discount_price"], "120.00")
        self.assertEqual(item["total_price"], "240.00")

        self.assertEqual(data["totals"]["subtotal"], "300.00")
        self.assertEqual(data["totals"]["discount_total"], "60.00")
        self.assertEqual(data["totals"]["grand_total"], "240.00")

        self.assertEqual(data["address"]["full_name"], "Test User")

        self.assertIn("lifecycle", data)
        self.assertIn("confirmed_at", data["lifecycle"])
        self.assertIn("processing_at", data["lifecycle"])
        self.assertIn("shipped_at", data["lifecycle"])

        self.assertEqual(len(data["events"]), 1)
        event = data["events"][0]

        self.assertEqual(event["event_type"], OrderEvent.TYPE_CREATED)
        self.assertEqual(str(event["performed_by"]), str(self.customer.id))

        self.assertEqual(len(data["notes"]), 1)
        note = data["notes"][0]

        self.assertEqual(str(note["author"]), str(self.customer.id))
        self.assertEqual(note["message"], "Test note")

    def test_management_detail_returns_404_when_order_not_found(self):
        self.authenticate(self.staff)

        url = reverse(self.url_name, kwargs={"order_id": uuid4()})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    def test_management_detail_returns_correct_order_when_multiple_exist(self):
        self.authenticate(self.staff)

        other_order = self.create_order_with_full_data(customer=self.customer)
        target_order = self.create_order_with_full_data(customer=self.customer)

        url = reverse(self.url_name, kwargs={"order_id": target_order.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(target_order.id))
        self.assertNotEqual(response.data["id"], str(other_order.id))

    def test_management_detail_contains_timestamp_fields(self):
        self.authenticate(self.staff)

        order = self.create_order_with_full_data(customer=self.customer)

        url = reverse(self.url_name, kwargs={"order_id": order.id})

        response = self.client.get(url)

        data = response.data

        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

        self.assertIn("created_at", data["items"][0])
        self.assertIn("updated_at", data["totals"])
        self.assertIn("created_at", data["address"])
        self.assertIn("created_at", data["events"][0])
        self.assertIn("created_at", data["notes"][0])