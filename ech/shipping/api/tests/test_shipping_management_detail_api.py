import uuid
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from ech.users.models import CustomUser
from ech.orders.models import Order
from ech.shipping.models import (
    Shipment,
    ShipmentAddress,
    ShipmentLifecycle,
)


class ShipmentManagementDetailApiTestCase(APITestCase):
    def setUp(self):
        self.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.staff = CustomUser.objects.create_user(
            email="ops@company.com",
            password="StrongPassword123",
            user_name="Operations Staff",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            is_active=True,
            email_confirmed=True,
        )

        self.admin = CustomUser.objects.create_user(
            email="admin@company.com",
            password="StrongPassword123",
            user_name="Admin User",
            role=CustomUser.ROLE_ADMIN,
            is_active=True,
            email_confirmed=True,
        )

        self.order = self._create_order(customer=self.customer)

        self.shipment = self._create_shipment(
            order=self.order,
            customer=self.customer,
        )

        self.url = reverse(
            "shipping-api:shipment-management-detail",
            kwargs={"shipment_id": self.shipment.id},
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def _create_order(self, *, customer):
        """Create a minimal valid order."""
        return Order.objects.create(
            customer=customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
            currency="USD",
        )

    def _create_shipment(self, *, order, customer):
        """Create a shipment with required related models."""
        shipment = Shipment.objects.create(
            order=order,
            customer=customer,
            status="pending",
            shipping_method="standard",
            carrier_name="DHL",
            tracking_code="TRACK-MGMT-DETAIL",
            external_reference="EXT-MGMT-DETAIL",
            shipping_cost="10.00",
            currency="USD",
            estimated_delivery_date=timezone.localdate() + timedelta(days=5),
            idempotency_key=uuid.uuid4(),
        )

        ShipmentAddress.objects.create(
            shipment=shipment,
            full_name="John Doe",
            address_line="123 Main Street",
            city="Sao Paulo",
            state="SP",
            country="Brazil",
            postal_code="01000-000",
            phone="11999999999",
            delivery_instructions="Leave at reception",
        )

        ShipmentLifecycle.objects.create(shipment=shipment)

        return shipment

    def test_management_detail_requires_authentication(self):
        """Reject management detail for unauthenticated users."""
        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_management_detail_rejects_customer_user(self):
        """Reject management detail access for customer users."""
        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_management_detail_allows_staff_user(self):
        """Allow staff users to access shipment management detail."""
        self.authenticate(self.staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.shipment.id))
        self.assertEqual(response.data["customer"], self.customer.id)

    def test_management_detail_allows_admin_user(self):
        """Allow admin users to access shipment management detail."""
        self.authenticate(self.admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.shipment.id))
        self.assertEqual(response.data["customer"], self.customer.id)

    def test_management_detail_returns_404_for_nonexistent_shipment(self):
        """Return 404 when shipment does not exist."""
        self.authenticate(self.staff)

        url = reverse(
            "shipping-api:shipment-management-detail",
            kwargs={"shipment_id": uuid.uuid4()},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_management_detail_returns_expected_fields(self):
        """Return expected fields in shipment management detail response."""
        self.authenticate(self.staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("id", response.data)
        self.assertIn("order", response.data)
        self.assertIn("customer", response.data)
        self.assertIn("status", response.data)
        self.assertIn("shipping_method", response.data)
        self.assertIn("carrier_name", response.data)
        self.assertIn("tracking_code", response.data)
        self.assertIn("external_reference", response.data)
        self.assertIn("shipping_cost", response.data)
        self.assertIn("currency", response.data)
        self.assertIn("estimated_delivery_date", response.data)
        self.assertIn("address", response.data)
        self.assertIn("lifecycle", response.data)