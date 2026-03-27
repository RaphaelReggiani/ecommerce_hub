from decimal import Decimal
import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ech.users.models import CustomUser
from ech.orders.models import Order
from ech.shipping.models import (
    Shipment,
    ShipmentAddress,
    ShipmentLifecycle,
    ShipmentEvent,
)


class ShipmentCreateApiTestCase(APITestCase):
    def setUp(self):
        self.url = reverse("shipping-api:shipment-create")

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

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def _create_order(self, *, customer):
        """
        Create a minimal valid order instance for shipment tests.
        """
        return Order.objects.create(
            customer=customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
            currency="USD",
        )

    def _build_payload(self, **overrides):
        payload = {
            "order_id": str(self.order.id),
            "shipping_method": "standard",
            "shipping_cost": "25.00",
            "currency": "USD",
            "carrier_name": "DHL",
            "tracking_code": "TRACK-123456",
            "external_reference": "EXT-REF-001",
            "estimated_delivery_date": "2026-04-05",
            "idempotency_key": str(uuid.uuid4()),
            "address_data": {
                "full_name": "John Doe",
                "address_line": "123 Main Street",
                "city": "Sao Paulo",
                "state": "SP",
                "country": "Brazil",
                "postal_code": "01000-000",
                "phone": "11999999999",
                "delivery_instructions": "Leave at front desk",
            },
        }
        payload.update(overrides)
        return payload

    def test_create_shipment_returns_unauthorized_for_unauthenticated_user(self):
        """Reject shipment creation for unauthenticated users."""
        payload = self._build_payload()

        response = self.client.post(self.url, payload, format="json")

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )
        self.assertEqual(Shipment.objects.count(), 0)

    def test_create_shipment_successfully_as_operations_staff(self):
        """Allow shipment creation for operations staff users."""
        self.authenticate(self.operations_staff)
        payload = self._build_payload()

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Shipment.objects.count(), 1)

        shipment = Shipment.objects.select_related(
            "address",
            "lifecycle",
        ).get()

        self.assertEqual(shipment.order, self.order)
        self.assertEqual(shipment.customer, self.customer)
        self.assertEqual(shipment.status, Shipment.STATUS_PENDING)
        self.assertEqual(shipment.shipping_method, "standard")
        self.assertEqual(shipment.carrier_name, "DHL")
        self.assertEqual(shipment.tracking_code, "TRACK-123456")
        self.assertEqual(shipment.external_reference, "EXT-REF-001")
        self.assertEqual(shipment.shipping_cost, Decimal("25.00"))
        self.assertEqual(shipment.currency, "USD")
        self.assertEqual(
            str(shipment.idempotency_key),
            payload["idempotency_key"],
        )

        self.assertTrue(
            ShipmentAddress.objects.filter(shipment=shipment).exists()
        )
        self.assertTrue(
            ShipmentLifecycle.objects.filter(shipment=shipment).exists()
        )
        self.assertTrue(
            ShipmentEvent.objects.filter(shipment=shipment).exists()
        )

        self.assertEqual(response.data["id"], str(shipment.id))
        self.assertEqual(response.data["status"], Shipment.STATUS_PENDING)

    def test_create_shipment_successfully_as_admin(self):
        """Allow shipment creation for admin users."""
        self.authenticate(self.admin)
        payload = self._build_payload()

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Shipment.objects.count(), 1)

    def test_create_shipment_rejects_customer_user(self):
        """Reject shipment creation for customer users."""
        self.authenticate(self.customer)
        payload = self._build_payload()

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Shipment.objects.count(), 0)

    def test_create_shipment_rejects_invalid_order(self):
        """Reject shipment creation when the order does not exist."""
        self.authenticate(self.operations_staff)
        payload = self._build_payload(order_id=str(uuid.uuid4()))

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Shipment.objects.count(), 0)

    def test_create_shipment_rejects_duplicate_shipment_for_same_order(self):
        """Reject shipment creation if the order already has a shipment."""
        self.authenticate(self.operations_staff)

        first_payload = self._build_payload()
        first_response = self.client.post(self.url, first_payload, format="json")

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Shipment.objects.count(), 1)

        second_payload = self._build_payload(
            idempotency_key=str(uuid.uuid4())
        )
        response = self.client.post(self.url, second_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Shipment.objects.count(), 1)

    def test_create_shipment_is_idempotent(self):
        """Return the existing shipment for repeated idempotent requests."""
        self.authenticate(self.operations_staff)

        idem_key = str(uuid.uuid4())
        payload = self._build_payload(idempotency_key=idem_key)

        first_response = self.client.post(self.url, payload, format="json")
        second_response = self.client.post(self.url, payload, format="json")

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertIn(
            second_response.status_code,
            {status.HTTP_200_OK, status.HTTP_201_CREATED},
        )
        self.assertEqual(Shipment.objects.count(), 1)

        shipment = Shipment.objects.get()
        self.assertEqual(str(shipment.idempotency_key), idem_key)

    def test_create_shipment_rejects_missing_required_fields(self):
        """Reject shipment creation when required fields are missing."""
        self.authenticate(self.operations_staff)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Shipment.objects.count(), 0)