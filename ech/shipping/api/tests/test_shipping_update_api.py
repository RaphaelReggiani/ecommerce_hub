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


class ShipmentUpdateApiTestCase(APITestCase):
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
        )

        self.url = reverse(
            "shipping-api:shipment-update",
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
            status="pending",
            shipping_method="standard",
            carrier_name="DHL",
            tracking_code="TRACK-UPDATE",
            external_reference="EXT-UPDATE",
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

    def test_update_shipment_returns_unauthorized_for_unauthenticated_user(self):
        """Reject shipment update for unauthenticated users."""
        payload = {
            "shipment_data": {
                "carrier_name": "FedEx",
            }
        }

        response = self.client.patch(self.url, payload, format="json")

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_update_shipment_rejects_customer_user(self):
        """Reject shipment update for customer users."""
        self.authenticate(self.customer)

        payload = {
            "shipment_data": {
                "carrier_name": "FedEx",
            }
        }

        response = self.client.patch(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_shipment_successfully_as_operations_staff(self):
        """Allow shipment update by operations staff."""
        self.authenticate(self.operations_staff)

        payload = {
            "shipment_data": {
                "carrier_name": "FedEx",
                "tracking_code": "TRACK-UPDATED",
            }
        }

        response = self.client.patch(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.shipment.refresh_from_db()

        self.assertEqual(self.shipment.carrier_name, "FedEx")
        self.assertEqual(self.shipment.tracking_code, "TRACK-UPDATED")

    def test_update_shipment_successfully_as_admin(self):
        """Allow shipment update by admin users."""
        self.authenticate(self.admin)

        payload = {
            "shipment_data": {
                "carrier_name": "UPS",
            }
        }

        response = self.client.patch(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.shipment.refresh_from_db()

        self.assertEqual(self.shipment.carrier_name, "UPS")

    def test_update_shipment_updates_address_snapshot(self):
        """Allow updating shipment address snapshot."""
        self.authenticate(self.operations_staff)

        payload = {
            "address_data": {
                "full_name": "John Doe",
                "address_line": "123 Main Street",
                "city": "Rio de Janeiro",
                "state": "RJ",
                "country": "Brazil",
                "postal_code": "01000-000",
                "phone": "11999999999",
                "delivery_instructions": "Leave at reception",
            }
        }

        response = self.client.patch(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        address = ShipmentAddress.objects.get(shipment=self.shipment)

        self.assertEqual(address.city, "Rio de Janeiro")
        self.assertEqual(address.state, "RJ")

    def test_update_shipment_rejects_update_when_status_locked(self):
        """Reject shipment update when shipment is already delivered."""
        self.authenticate(self.operations_staff)

        self.shipment.status = "delivered"
        self.shipment.save()

        payload = {
            "shipment_data": {
                "carrier_name": "FedEx",
            }
        }

        response = self.client.patch(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_shipment_returns_404_for_nonexistent_shipment(self):
        """Return 404 when shipment does not exist."""
        self.authenticate(self.operations_staff)

        url = reverse(
            "shipping-api:shipment-update",
            kwargs={"shipment_id": uuid.uuid4()},
        )

        payload = {
            "shipment_data": {
                "carrier_name": "UPS",
            }
        }

        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_shipment_rejects_invalid_payload(self):
        """Reject shipment update when payload contains invalid field types."""
        self.authenticate(self.operations_staff)

        payload = {
            "shipment_data": {
                "shipping_cost": "invalid-value",
            }
        }

        response = self.client.patch(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)