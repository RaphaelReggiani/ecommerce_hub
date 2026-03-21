import uuid

from django.test import TestCase, override_settings
from django.core.cache import cache

from ech.payments.services.cache_service import PaymentCacheService
from ech.payments.utils.cache_keys import PaymentCacheKeys


TEST_CACHE = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}


@override_settings(CACHES=TEST_CACHE)
class PaymentCacheSelectorsTestCase(TestCase):

    def setUp(self):
        cache.clear()
        self.payment_id = uuid.uuid4()
        self.customer_id = uuid.uuid4()

    def test_build_key_adds_version_prefix(self):
        """Ensure cache key is prefixed with version."""
        raw_key = "payment:test"

        built = PaymentCacheService._build_key(raw_key)

        self.assertTrue(built.startswith(f"{PaymentCacheService.VERSION}:"))

    def test_set_and_get_value(self):
        """Ensure set stores value and get retrieves it."""
        key = "test:key"
        value = {"test": 1}

        PaymentCacheService.set(key, value, timeout=60)

        cached = PaymentCacheService.get(key)

        self.assertEqual(cached, value)

    def test_delete_removes_cached_value(self):
        """Ensure delete removes cached key."""
        key = "test:key"

        PaymentCacheService.set(key, "value", timeout=60)
        PaymentCacheService.delete(key)

        cached = PaymentCacheService.get(key)

        self.assertIsNone(cached)

    def test_get_or_set_executes_factory_when_cache_empty(self):
        """Ensure get_or_set evaluates factory when cache miss occurs."""

        key = "test:key"

        def factory():
            return {"value": 123}

        result = PaymentCacheService.get_or_set(key, factory, timeout=60)

        self.assertEqual(result, {"value": 123})

    def test_get_or_set_returns_cached_value(self):
        """Ensure get_or_set returns cached value without calling factory."""

        key = "test:key"

        PaymentCacheService.set(key, {"cached": True}, timeout=60)

        called = False

        def factory():
            nonlocal called
            called = True
            return {}

        result = PaymentCacheService.get_or_set(key, factory, timeout=60)

        self.assertEqual(result, {"cached": True})
        self.assertFalse(called)

    def test_payment_detail_cache_helpers(self):
        """Ensure payment detail helpers store and retrieve cached values."""

        value = {"payment": "detail"}

        PaymentCacheService.set_payment_detail(self.payment_id, value)

        cached = PaymentCacheService.get_payment_detail(self.payment_id)

        self.assertEqual(cached, value)

    def test_customer_payments_cache_helpers(self):
        """Ensure customer payments cache helpers work correctly."""

        value = ["payment1", "payment2"]

        PaymentCacheService.set_customer_payments(self.customer_id, page=1, value=value)

        cached = PaymentCacheService.get_customer_payments(self.customer_id, page=1)

        self.assertEqual(cached, value)

    def test_management_payments_cache_helpers(self):
        """Ensure management payment list helpers cache values correctly."""

        value = ["paymentA"]

        PaymentCacheService.set_management_payments(page=1, value=value)

        cached = PaymentCacheService.get_management_payments(page=1)

        self.assertEqual(cached, value)

    def test_payment_transactions_cache_helpers(self):
        """Ensure payment transaction cache helpers store values."""

        value = ["tx1", "tx2"]

        PaymentCacheService.set_payment_transactions(self.payment_id, value)

        cached = PaymentCacheService.get_payment_transactions(self.payment_id)

        self.assertEqual(cached, value)

    def test_payment_refunds_cache_helpers(self):
        """Ensure payment refund cache helpers store values."""

        value = ["refund1"]

        PaymentCacheService.set_payment_refunds(self.payment_id, value)

        cached = PaymentCacheService.get_payment_refunds(self.payment_id)

        self.assertEqual(cached, value)