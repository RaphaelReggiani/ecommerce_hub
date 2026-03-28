from datetime import timedelta
import uuid

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


class ShipmentListApiTestCase(APITestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse("shipping-api:shipment-list")

        self.customer = CustomUser.objects.create_user(
            email="customer@test.com",
            password="StrongPassword123",
            user_name="Customer User",
            role=CustomUser.ROLE_CUSTOMER_USER,
            is_active=True,
            email_confirmed=True,
        )

        self.other_customer = CustomUser.objects.create_user(
            email="other_customer@test.com",
            password="StrongPassword123",
            user_name="Other Customer",
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

        self.order_1 = self._create_order(customer=self.customer)
        self.order_2 = self._create_order(customer=self.customer)
        self.order_3 = self._create_order(customer=self.other_customer)

        self.shipment_1 = self._create_shipment(
            order=self.order_1,
            customer=self.customer,
            status="pending",
            shipping_method="standard",
            carrier_name="DHL",
            tracking_code="TRACK-AAA",
            external_reference="EXT-AAA",
        )

        self.shipment_2 = self._create_shipment(
            order=self.order_2,
            customer=self.customer,
            status="in_transit",
            shipping_method="express",
            carrier_name="FedEx",
            tracking_code="TRACK-BBB",
            external_reference="EXT-BBB",
        )

        self._create_shipment(
            order=self.order_3,
            customer=self.other_customer,
            status="delivered",
            shipping_method="same_day",
            carrier_name="UPS",
            tracking_code="TRACK-CCC",
            external_reference="EXT-CCC",
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def _create_order(self, *, customer):
        """
        Create a minimal valid order instance for shipment list tests.
        """
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
        status,
        shipping_method,
        carrier_name,
        tracking_code,
        external_reference,
    ):
        """
        Create a shipment with related address and lifecycle records.
        """
        shipment = Shipment.objects.create(
            order=order,
            customer=customer,
            status=status,
            shipping_method=shipping_method,
            carrier_name=carrier_name,
            tracking_code=tracking_code,
            external_reference=external_reference,
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
            delivery_instructions="Leave at front desk",
        )

        ShipmentLifecycle.objects.create(shipment=shipment)

        return shipment

    def test_list_shipments_returns_unauthorized_for_unauthenticated_user(self):
        """Reject shipment listing for unauthenticated users."""
        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def test_list_shipments_returns_only_authenticated_customer_shipments(self):
        """Return only shipments owned by the authenticated customer."""
        self.authenticate(self.customer)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)

        returned_ids = {item["id"] for item in response.data["results"]}

        self.assertIn(str(self.shipment_1.id), returned_ids)
        self.assertIn(str(self.shipment_2.id), returned_ids)

    def test_list_shipments_excludes_shipments_from_other_customers(self):
        """Exclude shipments that belong to other customers."""
        self.authenticate(self.customer)

        response = self.client.get(self.url)

        returned_customer_ids = {
            item["customer"] for item in response.data["results"]
        }

        self.assertEqual(returned_customer_ids, {self.customer.id})

    def test_list_shipments_returns_empty_result_for_staff_without_owned_shipments(self):
        """Return an empty shipment list for staff users without owned shipments."""
        self.authenticate(self.operations_staff)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])

    def test_list_shipments_supports_status_filter(self):
        """Filter customer shipments by status."""
        self.authenticate(self.customer)

        response = self.client.get(self.url, {"status": "in_transit"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(self.shipment_2.id),
        )
        self.assertEqual(
            response.data["results"][0]["status"],
            "in_transit",
        )

    def test_list_shipments_supports_shipping_method_filter(self):
        """Filter customer shipments by shipping method."""
        self.authenticate(self.customer)

        response = self.client.get(self.url, {"shipping_method": "standard"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(self.shipment_1.id),
        )
        self.assertEqual(
            response.data["results"][0]["shipping_method"],
            "standard",
        )

    def test_list_shipments_supports_carrier_name_filter(self):
        """Filter customer shipments by partial carrier name."""
        self.authenticate(self.customer)

        response = self.client.get(self.url, {"carrier_name": "fed"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(self.shipment_2.id),
        )
        self.assertEqual(
            response.data["results"][0]["carrier_name"],
            "FedEx",
        )

    def test_list_shipments_supports_tracking_code_filter(self):
        """Filter customer shipments by partial tracking code."""
        self.authenticate(self.customer)

        response = self.client.get(self.url, {"tracking_code": "AAA"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(self.shipment_1.id),
        )
        self.assertEqual(
            response.data["results"][0]["tracking_code"],
            "TRACK-AAA",
        )

    def test_list_shipments_supports_pagination(self):
        """Paginate shipment list results when page_size is provided."""
        self.authenticate(self.customer)

        response = self.client.get(self.url, {"page_size": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)