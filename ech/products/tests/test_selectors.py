from decimal import Decimal
import uuid
from django.test import TestCase

from ech.users.models import CustomUser
from ech.products.models import Product, ProductInventory
from ech.products.selectors import (
    get_product_by_id,
    get_active_product_by_id,
    get_all_active_products,
    get_products_by_type,
    get_products_with_discount,
    search_products,
    get_products_created_by_user,
    get_available_products,
)


class ProductSelectorsTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="staff@company.com",
            password="StrongPassword123",
            role=CustomUser.ROLE_OPERATIONS_STAFF,
            user_name="Staff User",
        )

        self.product_active = Product.objects.create(
            name="Gaming Mouse",
            product_type=Product.MOUSE,
            brand="Logitech",
            sold_by=self.user,
            description="Gaming mouse",
            technical_information="Specs",
            price=Decimal("200.00"),
            discount_price=Decimal("150.00"),
            is_active=True,
        )

        self.product_inactive = Product.objects.create(
            name="Old Keyboard",
            product_type=Product.KEYBOARD,
            brand="Razer",
            sold_by=self.user,
            description="Old keyboard",
            technical_information="Specs",
            price=Decimal("300.00"),
            is_active=False,
        )

        ProductInventory.objects.create(
            product=self.product_active,
            quantity=10,
        )

    def test_get_product_by_id_returns_product(self):
        """Ensure get_product_by_id returns the correct product."""
        product = get_product_by_id(self.product_active.id)
        self.assertEqual(product, self.product_active)

    def test_get_product_by_id_returns_none_when_not_found(self):
        """Ensure get_product_by_id returns None when product does not exist."""
        product = get_product_by_id(uuid.uuid4())
        self.assertIsNone(product)

    def test_get_active_product_by_id_returns_only_active_product(self):
        """Ensure get_active_product_by_id returns only active products."""
        product = get_active_product_by_id(self.product_active.id)
        self.assertEqual(product, self.product_active)

    def test_get_active_product_by_id_returns_none_for_inactive_product(self):
        """Ensure get_active_product_by_id returns None for inactive product."""
        product = get_active_product_by_id(self.product_inactive.id)
        self.assertIsNone(product)

    def test_get_all_active_products_returns_only_active_products(self):
        """Ensure get_all_active_products returns only active products."""
        products = list(get_all_active_products())

        self.assertIn(self.product_active, products)
        self.assertNotIn(self.product_inactive, products)

    def test_get_products_by_type_filters_correctly(self):
        """Ensure get_products_by_type filters products by type."""
        products = list(get_products_by_type(Product.MOUSE))

        self.assertIn(self.product_active, products)
        self.assertNotIn(self.product_inactive, products)

    def test_get_products_with_discount_returns_only_discounted_products(self):
        """Ensure get_products_with_discount returns only products with discount."""
        products = list(get_products_with_discount())

        self.assertIn(self.product_active, products)
        self.assertNotIn(self.product_inactive, products)

    def test_search_products_finds_by_name(self):
        """Ensure search_products finds products by name."""
        results = list(search_products("Mouse"))

        self.assertIn(self.product_active, results)

    def test_search_products_finds_by_brand(self):
        """Ensure search_products finds products by brand."""
        results = list(search_products("Logitech"))

        self.assertIn(self.product_active, results)

    def test_search_products_is_case_insensitive(self):
        """Ensure search_products is case insensitive."""
        results = list(search_products("logitech"))

        self.assertIn(self.product_active, results)

    def test_search_products_returns_empty_when_no_match(self):
        """Ensure search_products returns empty queryset when no match is found."""
        results = list(search_products("NonExistent"))

        self.assertEqual(results, [])

    def test_get_products_created_by_user_returns_only_user_products(self):
        """Ensure get_products_created_by_user returns only products created by given user."""
        products = list(get_products_created_by_user(self.user))

        self.assertIn(self.product_active, products)
        self.assertIn(self.product_inactive, products)

    def test_get_available_products_returns_only_products_with_inventory(self):
        """Ensure get_available_products returns only products with inventory > 0."""
        products = list(get_available_products())

        self.assertIn(self.product_active, products)
        self.assertNotIn(self.product_inactive, products)

    def test_get_available_products_excludes_products_with_zero_inventory(self):
        """Ensure get_available_products excludes products with zero inventory."""
        product_no_inventory = Product.objects.create(
            name="Empty Stock Product",
            product_type=Product.MOUSE,
            brand="Brand",
            sold_by=self.user,
            description="Desc",
            technical_information="Specs",
            price=Decimal("100.00"),
            is_active=True,
        )

        ProductInventory.objects.create(
            product=product_no_inventory,
            quantity=0,
        )

        products = list(get_available_products())

        self.assertNotIn(product_no_inventory, products)