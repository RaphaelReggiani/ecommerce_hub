from decimal import Decimal

from django.test import TestCase

from ech.users.models import CustomUser
from ech.products.models import Product
from ech.products.filters import ProductFilter


class ProductFilterTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="filters@company.com",
            password="StrongPassword123",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            user_name="Filter User",
        )

        self.product_1 = Product.objects.create(
            name="Gaming Mouse",
            product_type=Product.MOUSE,
            brand="Logitech",
            sold_by=self.user,
            description="Desc",
            technical_information="Specs",
            price=Decimal("100.00"),
            is_active=True,
        )

        self.product_2 = Product.objects.create(
            name="Mechanical Keyboard",
            product_type=Product.KEYBOARD,
            brand="Keychron",
            sold_by=self.user,
            description="Desc",
            technical_information="Specs",
            price=Decimal("300.00"),
            is_active=True,
        )

        self.product_3 = Product.objects.create(
            name="Office Mouse",
            product_type=Product.MOUSE,
            brand="Logitech",
            sold_by=self.user,
            description="Desc",
            technical_information="Specs",
            price=Decimal("200.00"),
            is_active=True,
        )

    def test_filter_by_price_min(self):
        """Ensure filter returns products with price >= price_min."""
        filterset = ProductFilter(
            {"price_min": 200},
            queryset=Product.objects.all(),
        )

        results = list(filterset.qs)

        self.assertIn(self.product_2, results)
        self.assertIn(self.product_3, results)
        self.assertNotIn(self.product_1, results)

    def test_filter_by_price_max(self):
        """Ensure filter returns products with price <= price_max."""
        filterset = ProductFilter(
            {"price_max": 200},
            queryset=Product.objects.all(),
        )

        results = list(filterset.qs)

        self.assertIn(self.product_1, results)
        self.assertIn(self.product_3, results)
        self.assertNotIn(self.product_2, results)

    def test_filter_by_price_range(self):
        """Ensure filter returns products within a price range."""
        filterset = ProductFilter(
            {"price_min": 150, "price_max": 250},
            queryset=Product.objects.all(),
        )

        results = list(filterset.qs)

        self.assertIn(self.product_3, results)
        self.assertNotIn(self.product_1, results)
        self.assertNotIn(self.product_2, results)

    def test_filter_by_brand_case_insensitive(self):
        """Ensure filter by brand is case-insensitive."""
        filterset = ProductFilter(
            {"brand": "logitech"},
            queryset=Product.objects.all(),
        )

        results = list(filterset.qs)

        self.assertIn(self.product_1, results)
        self.assertIn(self.product_3, results)
        self.assertNotIn(self.product_2, results)

    def test_filter_by_product_type(self):
        """Ensure filter returns products of a specific type."""
        filterset = ProductFilter(
            {"product_type": Product.MOUSE},
            queryset=Product.objects.all(),
        )

        results = list(filterset.qs)

        self.assertIn(self.product_1, results)
        self.assertIn(self.product_3, results)
        self.assertNotIn(self.product_2, results)

    def test_filter_combined_filters(self):
        """Ensure filter works correctly with combined filters."""
        filterset = ProductFilter(
            {
                "product_type": Product.MOUSE,
                "price_min": 150,
                "brand": "logitech",
            },
            queryset=Product.objects.all(),
        )

        results = list(filterset.qs)

        self.assertIn(self.product_3, results)
        self.assertNotIn(self.product_1, results)
        self.assertNotIn(self.product_2, results)

    def test_filter_returns_empty_queryset_when_no_match(self):
        """Ensure filter returns empty queryset when no products match."""
        filterset = ProductFilter(
            {"brand": "NonExistentBrand"},
            queryset=Product.objects.all(),
        )

        results = list(filterset.qs)

        self.assertEqual(results, [])