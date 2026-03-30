import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from ech.products.models import (
    Product,
)
from ech.reviews.models import (
    Review, 
    ReviewLifecycle, 
    ReviewEvent,
)
from ech.reviews.selectors import (
    get_review_by_id,
    get_review_by_id_for_customer,
    get_review_by_idempotency_key,
    get_review_by_customer_and_product,
    get_review_lifecycle,
    list_reviews_for_customer,
    list_reviews_for_management,
    list_reviews_by_product,
    list_public_reviews_by_product,
    list_reviews_by_status,
    list_reviews_by_rating,
    list_verified_purchase_reviews,
    list_review_events,
    get_product_review_summary,
)
from ech.reviews.exceptions import ReviewNotFoundException


User = get_user_model()


class BaseSelectorFactoryMixin:
    def create_user(self, **kwargs):
        suffix = uuid.uuid4().hex[:8]
        role = kwargs.get("role", User.ROLE_CUSTOMER_USER)

        corporate_roles = {
            User.ROLE_SUPERADMIN,
            User.ROLE_ADMIN,
            User.ROLE_SUPPORT_STAFF,
            User.ROLE_OPERATIONS_STAFF,
        }

        domain = "company.com" if role in corporate_roles else "test.com"

        data = {
            "email": f"user_{suffix}@{domain}",
            "password": "StrongPassword123",
            "user_name": f"User {suffix}",
            "role": User.ROLE_CUSTOMER_USER,
            "is_active": True,
            "email_confirmed": True,
        }
        data.update(kwargs)
        return User.objects.create_user(**data)

    def create_product(self, **kwargs):
        suffix = uuid.uuid4().hex[:8]

        seller = kwargs.pop(
            "sold_by",
            None,
        ) or self.create_user(
            email=f"seller_{suffix}@company.com",
            user_name=f"Seller {suffix}",
            role=User.ROLE_ADMIN,
        )

        data = {
            "name": f"Test Product {suffix}",
            "product_type": Product.PHONE,
            "brand": "Test Brand",
            "sold_by": seller,
            "description": "Product description",
            "technical_information": "Technical info",
            "price": Decimal("10.00"),
        }
        data.update(kwargs)
        return Product.objects.create(**data)

    def create_review(self, **kwargs):
        customer = kwargs.pop("customer", None) or self.create_user()
        product = kwargs.pop("product", None) or self.create_product()

        data = {
            "customer": customer,
            "product": product,
            "rating": 5,
            "title": "Great",
            "comment": "Excellent product",
            "status": Review.REVIEW_STATUS_PENDING,
            "is_verified_purchase": False,
        }
        data.update(kwargs)

        review = Review.objects.create(**data)
        ReviewLifecycle.objects.create(review=review)

        return review


class ReviewSelectorsTestCase(BaseSelectorFactoryMixin, TestCase):
    def test_get_review_by_id_success(self):
        review = self.create_review()

        result = get_review_by_id(review.id)

        self.assertEqual(result.id, review.id)

    def test_get_review_by_id_not_found(self):
        with self.assertRaises(ReviewNotFoundException):
            get_review_by_id(uuid.uuid4())

    def test_get_review_by_id_for_customer_success(self):
        customer = self.create_user()
        review = self.create_review(customer=customer)

        result = get_review_by_id_for_customer(review.id, customer)

        self.assertEqual(result.id, review.id)

    def test_get_review_by_id_for_customer_wrong_customer(self):
        review = self.create_review()
        another_user = self.create_user()

        with self.assertRaises(ReviewNotFoundException):
            get_review_by_id_for_customer(review.id, another_user)

    def test_get_review_by_idempotency_key(self):
        key = uuid.uuid4()
        review = self.create_review(idempotency_key=key)

        result = get_review_by_idempotency_key(key)

        self.assertEqual(result.id, review.id)

    def test_get_review_by_idempotency_key_returns_none(self):
        result = get_review_by_idempotency_key(uuid.uuid4())

        self.assertIsNone(result)

    def test_get_review_by_customer_and_product(self):
        customer = self.create_user()
        product = self.create_product()
        review = self.create_review(customer=customer, product=product)

        result = get_review_by_customer_and_product(customer, product)

        self.assertEqual(result.id, review.id)

    def test_get_review_lifecycle(self):
        review = self.create_review()

        lifecycle = get_review_lifecycle(review)

        self.assertEqual(lifecycle.review_id, review.id)

    def test_list_reviews_for_customer(self):
        customer = self.create_user()

        self.create_review(customer=customer, product=self.create_product())
        self.create_review(customer=customer, product=self.create_product())

        reviews = list_reviews_for_customer(customer)

        self.assertEqual(reviews.count(), 2)

    def test_list_reviews_for_management(self):
        self.create_review(product=self.create_product())
        self.create_review(product=self.create_product())

        reviews = list_reviews_for_management()

        self.assertEqual(reviews.count(), 2)

    def test_list_reviews_by_product(self):
        product = self.create_product()

        self.create_review(product=product, customer=self.create_user())
        self.create_review(product=product, customer=self.create_user())

        reviews = list_reviews_by_product(product)

        self.assertEqual(reviews.count(), 2)

    def test_list_public_reviews_by_product(self):
        product = self.create_product()

        self.create_review(
            product=product,
            customer=self.create_user(),
            status=Review.REVIEW_STATUS_APPROVED,
        )
        self.create_review(
            product=product,
            customer=self.create_user(),
            status=Review.REVIEW_STATUS_PENDING,
        )

        reviews = list_public_reviews_by_product(product)

        self.assertEqual(reviews.count(), 1)

    def test_list_reviews_by_status(self):
        self.create_review(
            product=self.create_product(),
            status=Review.REVIEW_STATUS_PENDING,
        )
        self.create_review(
            product=self.create_product(),
            status=Review.REVIEW_STATUS_APPROVED,
        )

        reviews = list_reviews_by_status(Review.REVIEW_STATUS_APPROVED)

        self.assertEqual(reviews.count(), 1)

    def test_list_reviews_by_rating(self):
        self.create_review(product=self.create_product(), rating=5)
        self.create_review(product=self.create_product(), rating=4)

        reviews = list_reviews_by_rating(5)

        self.assertEqual(reviews.count(), 1)

    def test_list_verified_purchase_reviews(self):
        self.create_review(
            product=self.create_product(),
            is_verified_purchase=True,
        )
        self.create_review(
            product=self.create_product(),
            is_verified_purchase=False,
        )

        reviews = list_verified_purchase_reviews()

        self.assertEqual(reviews.count(), 1)

    def test_list_review_events(self):
        review = self.create_review()

        ReviewEvent.objects.create(
            review=review,
            event_type=ReviewEvent.TYPE_CREATED,
        )

        events = list_review_events(review)

        self.assertEqual(events.count(), 1)

    def test_get_product_review_summary(self):
        product = self.create_product()

        self.create_review(
            product=product,
            customer=self.create_user(),
            rating=5,
            status=Review.REVIEW_STATUS_APPROVED,
        )
        self.create_review(
            product=product,
            customer=self.create_user(),
            rating=4,
            status=Review.REVIEW_STATUS_APPROVED,
            is_verified_purchase=True,
        )

        summary = get_product_review_summary(product)

        self.assertEqual(summary["total_reviews"], 2)
        self.assertEqual(summary["rating_distribution"][5], 1)
        self.assertEqual(summary["rating_distribution"][4], 1)
        self.assertEqual(summary["rating_distribution"][1], 0)
        self.assertEqual(summary["product_id"], product.id)
        self.assertEqual(summary["verified_reviews"], 1)