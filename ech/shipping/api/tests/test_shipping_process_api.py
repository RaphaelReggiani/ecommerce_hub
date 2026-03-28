import uuid
from datetime import timedelta

from django.core.cache import cache

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


class ShipmentProcessApiTestCase(APITestCase):
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

        self.operations_staff = CustomUser.objects.create_user(
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
            status="pending",
        )

        self.url = reverse(
            "shipping-api:shipment-process",
            kwargs={"shipment_id": self.shipment.id},
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def _create_order(self, *, customer):
        """Create a minimal valid order instance."""
        return Order.objects.create(
            customer=customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
            currency="USD",
        )

    def _create_shipment(self, *, order, customer, status):
        """Create a shipment with address and lifecycle."""
        shipment = Shipment.objects.create(
            order=order,
            customer=customer,
            status=status,
            shipping_method="standard",
            carrier_name="DHL",
            tracking_code="TRACK-PROCESS",
            external_reference="EXT-PROCESS",
            shipping_cost="20.00",
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

    def test_process_shipment_returns_unauthorized_for_unauthenticated_user(self):
        """Reject shipment processing for unauthenticated users."""
        payload = {"new_status": "preparing"}

        response = self.client.post(self.url, payload, format="json")

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_process_shipment_rejects_customer_user(self):
        """Reject shipment processing for customer users."""
        self.authenticate(self.customer)

        payload = {"new_status": "preparing"}

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_process_shipment_successfully_as_operations_staff(self):
        """Allow valid shipment status transition by operations staff."""
        self.authenticate(self.operations_staff)

        payload = {
            "new_status": "preparing",
            "metadata": {"note": "Shipment is being prepared."},
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.shipment.refresh_from_db()

        self.assertEqual(self.shipment.status, "preparing")

        lifecycle = ShipmentLifecycle.objects.get(shipment=self.shipment)
        self.assertIsNotNone(lifecycle.preparing_at)

    def test_process_shipment_successfully_as_admin(self):
        """Allow valid shipment status transition by admin users."""
        self.authenticate(self.admin)

        payload = {"new_status": "preparing"}

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.shipment.refresh_from_db()
        self.assertEqual(self.shipment.status, "preparing")

    def test_process_shipment_rejects_invalid_transition(self):
        """Reject invalid shipment status transition."""
        self.authenticate(self.operations_staff)

        payload = {"new_status": "delivered"}

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.shipment.refresh_from_db()
        self.assertEqual(self.shipment.status, "pending")

    def test_process_shipment_rejects_terminal_delivered_shipment(self):
        """Reject processing when shipment is already delivered."""
        self.authenticate(self.operations_staff)

        self.shipment.status = "delivered"
        self.shipment.save()

        payload = {"new_status": "returned"}

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_process_shipment_returns_404_for_nonexistent_shipment(self):
        """Return 404 when shipment does not exist."""
        self.authenticate(self.operations_staff)

        url = reverse(
            "shipping-api:shipment-process",
            kwargs={"shipment_id": uuid.uuid4()},
        )

        payload = {"new_status": "preparing"}

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_process_shipment_rejects_missing_new_status(self):
        """Reject shipment processing when new_status is missing."""
        self.authenticate(self.operations_staff)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)