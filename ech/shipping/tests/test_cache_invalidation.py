import uuid
from datetime import timedelta

from django.core.cache import cache
from django.test import TransactionTestCase
from django.utils import timezone

from ech.users.models import CustomUser
from ech.orders.models import Order
from ech.shipping.models import (
    Shipment,
    ShipmentAddress,
    ShipmentLifecycle,
)
from ech.shipping.selectors import (
    get_shipment_by_id,
    list_customer_shipments,
    list_management_shipments,
)
from ech.shipping.services.shipping_creation_service import (
    ShippingCreationService,
)
from ech.shipping.services.shipping_update_service import (
    ShippingUpdateService,
)
from ech.shipping.services.shipping_status_service import (
    ShippingStatusService,
)
from ech.shipping.services.shipping_cancellation_service import (
    ShippingCancellationService,
)
from ech.shipping.services.shipping_tracking_service import (
    ShippingTrackingService,
)


class ShippingCacheInvalidationTestCase(TransactionTestCase):
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

        self.staff = CustomUser.objects.create_user(
            email="ops@company.com",
            password="StrongPassword123",
            user_name="Operations Staff",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            is_active=True,
            email_confirmed=True,
        )

        self.order = Order.objects.create(
            customer=self.customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
            currency="USD",
        )

        self.shipment = Shipment.objects.create(
            order=self.order,
            customer=self.customer,
            status="pending",
            shipping_method="standard",
            carrier_name="DHL",
            tracking_code="TRACK-OLD",
            external_reference="EXT-OLD",
            shipping_cost="10.00",
            currency="USD",
            estimated_delivery_date=timezone.localdate() + timedelta(days=5),
            idempotency_key=uuid.uuid4(),
        )

        ShipmentAddress.objects.create(
            shipment=self.shipment,
            full_name="John Doe",
            address_line="123 Main Street",
            city="Sao Paulo",
            state="SP",
            country="Brazil",
            postal_code="01000-000",
        )

        ShipmentLifecycle.objects.create(shipment=self.shipment)

    def _new_order(self):
        return Order.objects.create(
            customer=self.customer,
            status=Order.ORDER_STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            shipping_status=Order.SHIPPING_STATUS_PENDING,
            currency="USD",
        )

    def test_creation_service_invalidates_customer_and_management_lists(self):
        """Invalidate list caches after shipment creation."""
        customer_before = list(list_customer_shipments(customer=self.customer))
        management_before = list(list_management_shipments())

        self.assertEqual(len(customer_before), 1)
        self.assertEqual(len(management_before), 1)

        new_order = self._new_order()

        ShippingCreationService.create_shipment(
            order=new_order,
            customer=self.customer,
            shipping_method="standard",
            address_data={
                "full_name": "Jane Doe",
                "address_line": "456 New Street",
                "city": "Rio de Janeiro",
                "state": "RJ",
                "country": "Brazil",
                "postal_code": "20000-000",
            },
            shipping_cost="12.00",
            currency="USD",
            performed_by=self.staff,
            idempotency_key=uuid.uuid4(),
        )

        customer_after = list(list_customer_shipments(customer=self.customer))
        management_after = list(list_management_shipments())

        self.assertEqual(len(customer_after), 2)
        self.assertEqual(len(management_after), 2)

    def test_update_service_invalidates_detail_cache(self):
        """Invalidate shipment detail cache after shipment update."""
        cached_shipment = get_shipment_by_id(shipment_id=self.shipment.id)
        self.assertEqual(cached_shipment.carrier_name, "DHL")

        ShippingUpdateService.update_shipment(
            shipment=self.shipment,
            shipment_data={"carrier_name": "FedEx"},
            performed_by=self.staff,
        )

        fresh_shipment = get_shipment_by_id(shipment_id=self.shipment.id)
        self.assertEqual(fresh_shipment.carrier_name, "FedEx")

    def test_status_service_invalidates_detail_cache(self):
        """Invalidate shipment detail cache after status transition."""
        cached_shipment = get_shipment_by_id(shipment_id=self.shipment.id)
        self.assertEqual(cached_shipment.status, "pending")

        ShippingStatusService.update_status(
            shipment=self.shipment,
            new_status="preparing",
            performed_by=self.staff,
        )

        fresh_shipment = get_shipment_by_id(shipment_id=self.shipment.id)
        self.assertEqual(fresh_shipment.status, "preparing")

    def test_cancellation_service_invalidates_detail_cache(self):
        """Invalidate shipment detail cache after shipment cancellation."""
        cached_shipment = get_shipment_by_id(shipment_id=self.shipment.id)
        self.assertEqual(cached_shipment.status, "pending")

        ShippingCancellationService.cancel_shipment(
            shipment=self.shipment,
            performed_by=self.staff,
        )

        fresh_shipment = get_shipment_by_id(shipment_id=self.shipment.id)
        self.assertEqual(fresh_shipment.status, "cancelled")

    def test_tracking_service_invalidates_detail_cache(self):
        """Invalidate shipment detail cache after tracking update."""
        self.shipment.status = "shipped"
        self.shipment.save(update_fields=["status"])

        cached_shipment = get_shipment_by_id(shipment_id=self.shipment.id)
        self.assertEqual(cached_shipment.status, "shipped")

        ShippingTrackingService.register_tracking_update(
            shipment=self.shipment,
            description="Shipment arrived at local hub",
            event_at=timezone.now(),
            status="in_transit",
            location="Sao Paulo Hub",
            performed_by=self.staff,
        )

        fresh_shipment = get_shipment_by_id(shipment_id=self.shipment.id)
        self.assertEqual(fresh_shipment.status, "in_transit")