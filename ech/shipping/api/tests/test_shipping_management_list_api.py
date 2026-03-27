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


class ShipmentManagementListApiTestCase(APITestCase):
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

        self.url = reverse("shipping-api:shipment-management-list")

        self.order_1 = self._create_order(customer=self.customer)
        self.order_2 = self._create_order(customer=self.customer)

        self.shipment_1 = self._create_shipment(
            order=self.order_1,
            customer=self.customer,
            carrier_name="DHL",
            tracking_code="TRACK-001",
            status="pending",
        )

        self.shipment_2 = self._create_shipment(
            order=self.order_2,
            customer=self.customer,
            carrier_name="FedEx",
            tracking_code="TRACK-002",
            status="shipped",
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

    def _create_shipment(
        self,
        *,
        order,
        customer,
        carrier_name,
        tracking_code,
        status,
    ):
        """Create a shipment with required related models."""
        shipment = Shipment.objects.create(
            order=order,
            customer=customer,
            status=status,
            shipping_method="standard",
            carrier_name=carrier_name,
            tracking_code=tracking_code,
            external_reference=f"EXT-{uuid.uuid4()}",
            shipping_cost="10.00",
            currency="USD",
            estimated_delivery_date=timezone.localdate()
            + timedelta(days=5),
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
        )

        ShipmentLifecycle.objects.create(shipment=shipment)

        return shipment

    def test_management_list_requires_authentication(self):
        """Reject management list for unauthenticated users."""
        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_management_list_rejects_customer_user(self):
        """Reject management list access for customer users."""
        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_management_list_returns_all_shipments_for_staff(self):
        """Allow staff users to list all shipments."""
        self.authenticate(self.staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_management_list_returns_all_shipments_for_admin(self):
        """Allow admin users to list all shipments."""
        self.authenticate(self.admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_management_list_supports_status_filter(self):
        """Filter shipments by status."""
        self.authenticate(self.staff)

        response = self.client.get(self.url, {"status": "pending"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_management_list_supports_carrier_name_filter(self):
        """Filter shipments by carrier name."""
        self.authenticate(self.staff)

        response = self.client.get(self.url, {"carrier_name": "DHL"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_management_list_supports_tracking_code_filter(self):
        """Filter shipments by tracking code."""
        self.authenticate(self.staff)

        response = self.client.get(self.url, {"tracking_code": "TRACK-002"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_management_list_supports_pagination(self):
        """Verify management list pagination."""
        self.authenticate(self.staff)

        response = self.client.get(self.url, {"page_size": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)