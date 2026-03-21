import uuid

from django.core.cache import cache
from django.test import TestCase, override_settings

from ech.payments.services.cache_service import PaymentCacheService


TEST_CACHE = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}


@override_settings(CACHES=TEST_CACHE)
class PaymentCacheInvalidationTestCase(TestCase):
    def setUp(self):
        cache.clear()
        self.payment_id = uuid.uuid4()
        self.customer_id = uuid.uuid4()
        self.payment_reference = "PAY-001"
        self.status = "pending"
        self.method = "pix"

    def test_invalidate_payment_detail_cache_removes_detail_reference_transactions_and_refunds(self):
        """Ensure payment detail invalidation removes all direct payment-related cache entries."""
        PaymentCacheService.set_payment_detail(self.payment_id, {"detail": True})
        PaymentCacheService.set_payment_by_reference(self.payment_reference, {"ref": True})
        PaymentCacheService.set_payment_transactions(self.payment_id, ["tx1"])
        PaymentCacheService.set_payment_refunds(self.payment_id, ["refund1"])

        PaymentCacheService.invalidate_payment_detail_cache(
            payment_id=self.payment_id,
            payment_reference=self.payment_reference,
        )

        self.assertIsNone(PaymentCacheService.get_payment_detail(self.payment_id))
        self.assertIsNone(PaymentCacheService.get_payment_by_reference(self.payment_reference))
        self.assertIsNone(PaymentCacheService.get_payment_transactions(self.payment_id))
        self.assertIsNone(PaymentCacheService.get_payment_refunds(self.payment_id))

    def test_invalidate_payment_detail_cache_without_reference_keeps_unrelated_reference_cache(self):
        """Ensure payment detail invalidation does not remove reference cache when reference is not provided."""
        PaymentCacheService.set_payment_detail(self.payment_id, {"detail": True})
        PaymentCacheService.set_payment_by_reference(self.payment_reference, {"ref": True})
        PaymentCacheService.set_payment_transactions(self.payment_id, ["tx1"])
        PaymentCacheService.set_payment_refunds(self.payment_id, ["refund1"])

        PaymentCacheService.invalidate_payment_detail_cache(
            payment_id=self.payment_id,
            payment_reference=None,
        )

        self.assertIsNone(PaymentCacheService.get_payment_detail(self.payment_id))
        self.assertEqual(
            PaymentCacheService.get_payment_by_reference(self.payment_reference),
            {"ref": True},
        )
        self.assertIsNone(PaymentCacheService.get_payment_transactions(self.payment_id))
        self.assertIsNone(PaymentCacheService.get_payment_refunds(self.payment_id))

    def test_invalidate_customer_payment_cache_removes_customer_page_cache(self):
        """Ensure customer payment cache invalidation removes cached list for informed page."""
        PaymentCacheService.set_customer_payments(
            self.customer_id,
            page=2,
            value=["payment1", "payment2"],
        )

        PaymentCacheService.invalidate_customer_payment_cache(
            customer_id=self.customer_id,
            page=2,
        )

        self.assertIsNone(
            PaymentCacheService.get_customer_payments(self.customer_id, page=2)
        )

    def test_invalidate_management_payment_cache_removes_management_page_cache(self):
        """Ensure management payment cache invalidation removes cached list for informed page."""
        PaymentCacheService.set_management_payments(page=3, value=["paymentA"])

        PaymentCacheService.invalidate_management_payment_cache(page=3)

        self.assertIsNone(PaymentCacheService.get_management_payments(page=3))

    def test_invalidate_filtered_payment_cache_removes_status_and_method_cache(self):
        """Ensure filtered cache invalidation removes both status and method caches when provided."""
        PaymentCacheService.set_payments_by_status(self.status, page=1, value=["p1"])
        PaymentCacheService.set_payments_by_method(self.method, page=1, value=["p2"])

        PaymentCacheService.invalidate_filtered_payment_cache(
            status=self.status,
            method=self.method,
            page=1,
        )

        self.assertIsNone(PaymentCacheService.get_payments_by_status(self.status, page=1))
        self.assertIsNone(PaymentCacheService.get_payments_by_method(self.method, page=1))

    def test_invalidate_filtered_payment_cache_only_removes_status_when_only_status_given(self):
        """Ensure filtered cache invalidation removes only status cache when method is not provided."""
        PaymentCacheService.set_payments_by_status(self.status, page=1, value=["p1"])
        PaymentCacheService.set_payments_by_method(self.method, page=1, value=["p2"])

        PaymentCacheService.invalidate_filtered_payment_cache(
            status=self.status,
            method=None,
            page=1,
        )

        self.assertIsNone(PaymentCacheService.get_payments_by_status(self.status, page=1))
        self.assertEqual(
            PaymentCacheService.get_payments_by_method(self.method, page=1),
            ["p2"],
        )

    def test_invalidate_filtered_payment_cache_only_removes_method_when_only_method_given(self):
        """Ensure filtered cache invalidation removes only method cache when status is not provided."""
        PaymentCacheService.set_payments_by_status(self.status, page=1, value=["p1"])
        PaymentCacheService.set_payments_by_method(self.method, page=1, value=["p2"])

        PaymentCacheService.invalidate_filtered_payment_cache(
            status=None,
            method=self.method,
            page=1,
        )

        self.assertEqual(
            PaymentCacheService.get_payments_by_status(self.status, page=1),
            ["p1"],
        )
        self.assertIsNone(PaymentCacheService.get_payments_by_method(self.method, page=1))

    def test_invalidate_payment_related_cache_removes_all_known_related_entries(self):
        """Ensure aggregate payment cache invalidation removes direct, customer, management, and filtered caches."""
        PaymentCacheService.set_payment_detail(self.payment_id, {"detail": True})
        PaymentCacheService.set_payment_by_reference(self.payment_reference, {"ref": True})
        PaymentCacheService.set_payment_transactions(self.payment_id, ["tx1"])
        PaymentCacheService.set_payment_refunds(self.payment_id, ["refund1"])
        PaymentCacheService.set_customer_payments(self.customer_id, page=1, value=["c1"])
        PaymentCacheService.set_management_payments(page=1, value=["m1"])
        PaymentCacheService.set_payments_by_status(self.status, page=1, value=["s1"])
        PaymentCacheService.set_payments_by_method(self.method, page=1, value=["pm1"])

        PaymentCacheService.invalidate_payment_related_cache(
            payment_id=self.payment_id,
            customer_id=self.customer_id,
            payment_reference=self.payment_reference,
            status=self.status,
            method=self.method,
            page=1,
        )

        self.assertIsNone(PaymentCacheService.get_payment_detail(self.payment_id))
        self.assertIsNone(PaymentCacheService.get_payment_by_reference(self.payment_reference))
        self.assertIsNone(PaymentCacheService.get_payment_transactions(self.payment_id))
        self.assertIsNone(PaymentCacheService.get_payment_refunds(self.payment_id))
        self.assertIsNone(PaymentCacheService.get_customer_payments(self.customer_id, page=1))
        self.assertIsNone(PaymentCacheService.get_management_payments(page=1))
        self.assertIsNone(PaymentCacheService.get_payments_by_status(self.status, page=1))
        self.assertIsNone(PaymentCacheService.get_payments_by_method(self.method, page=1))

    def test_invalidate_payment_related_cache_without_optional_args_only_removes_mandatory_entries(self):
        """Ensure aggregate invalidation removes only mandatory caches when optional keys are not provided."""
        PaymentCacheService.set_payment_detail(self.payment_id, {"detail": True})
        PaymentCacheService.set_payment_transactions(self.payment_id, ["tx1"])
        PaymentCacheService.set_payment_refunds(self.payment_id, ["refund1"])
        PaymentCacheService.set_payment_by_reference(self.payment_reference, {"ref": True})
        PaymentCacheService.set_customer_payments(self.customer_id, page=1, value=["c1"])
        PaymentCacheService.set_management_payments(page=1, value=["m1"])
        PaymentCacheService.set_payments_by_status(self.status, page=1, value=["s1"])
        PaymentCacheService.set_payments_by_method(self.method, page=1, value=["pm1"])

        PaymentCacheService.invalidate_payment_related_cache(
            payment_id=self.payment_id,
            customer_id=None,
            payment_reference=None,
            status=None,
            method=None,
            page=1,
        )

        self.assertIsNone(PaymentCacheService.get_payment_detail(self.payment_id))
        self.assertIsNone(PaymentCacheService.get_payment_transactions(self.payment_id))
        self.assertIsNone(PaymentCacheService.get_payment_refunds(self.payment_id))
        self.assertEqual(
            PaymentCacheService.get_payment_by_reference(self.payment_reference),
            {"ref": True},
        )
        self.assertEqual(
            PaymentCacheService.get_customer_payments(self.customer_id, page=1),
            ["c1"],
        )
        self.assertIsNone(PaymentCacheService.get_management_payments(page=1))
        self.assertEqual(
            PaymentCacheService.get_payments_by_status(self.status, page=1),
            ["s1"],
        )
        self.assertEqual(
            PaymentCacheService.get_payments_by_method(self.method, page=1),
            ["pm1"],
        )