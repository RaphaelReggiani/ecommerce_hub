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
    ShipmentTrackingUpdate,
)


class ShipmentTrackingApiTestCase(APITestCase):
    def setUp(self):
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
        )

        self.url = reverse(
            "shipping-api:shipment-tracking",
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

    def _create_shipment(self, *, order, customer):
        """Create a shipment with address and lifecycle."""
        shipment = Shipment.objects.create(
            order=order,
            customer=customer,
            status="shipped",
            shipping_method="standard",
            carrier_name="DHL",
            tracking_code="TRACK-TRACKING",
            external_reference="EXT-TRACKING",
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

    def _build_payload(self, **overrides):
        payload = {
            "status": "in_transit",
            "description": "Shipment arrived at facility",
            "location": "Distribution Center",
            "event_at": timezone.now().isoformat(),
        }
        payload.update(overrides)
        return payload

    def test_tracking_update_returns_unauthorized_for_unauthenticated_user(self):
        """Reject tracking update for unauthenticated users."""
        payload = self._build_payload()

        response = self.client.post(self.url, payload, format="json")

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_tracking_update_rejects_customer_user(self):
        """Reject tracking update for customer users."""
        self.authenticate(self.customer)

        payload = self._build_payload()

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_tracking_update_successfully_as_operations_staff(self):
        """Allow tracking update by operations staff."""
        self.authenticate(self.operations_staff)

        payload = self._build_payload(
            status="in_transit",
            description="Shipment arrived at facility",
            location="Distribution Center",
        )

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.shipment.refresh_from_db()
        self.assertEqual(self.shipment.status, "in_transit")

        tracking_update = ShipmentTrackingUpdate.objects.filter(
            shipment=self.shipment
        ).first()

        self.assertIsNotNone(tracking_update)
        self.assertEqual(tracking_update.status, "in_transit")
        self.assertEqual(tracking_update.location, "Distribution Center")
        self.assertEqual(
            tracking_update.description,
            "Shipment arrived at facility",
        )

    def test_tracking_update_successfully_as_admin(self):
        """Allow tracking update by admin users."""
        self.authenticate(self.admin)

        payload = self._build_payload(
            status="in_transit",
            description="Shipment moved to sorting facility",
            location="Sorting Facility",
        )

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.shipment.refresh_from_db()
        self.assertEqual(self.shipment.status, "in_transit")

    def test_tracking_update_rejects_invalid_status(self):
        """Reject tracking update when status is invalid."""
        self.authenticate(self.operations_staff)

        payload = self._build_payload(status="invalid_status")

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tracking_update_rejects_missing_required_fields(self):
        """Reject tracking update when required fields are missing."""
        self.authenticate(self.operations_staff)

        payload = {
            "status": "in_transit",
            "location": "Distribution Center",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tracking_update_returns_404_for_nonexistent_shipment(self):
        """Return 404 when shipment does not exist."""
        self.authenticate(self.operations_staff)

        url = reverse(
            "shipping-api:shipment-tracking",
            kwargs={"shipment_id": uuid.uuid4()},
        )

        payload = self._build_payload()

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)