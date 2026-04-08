from collections import defaultdict
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from ech.analytics.constants.constants import (
    ANALYTIC_HIGH_RATING_THRESHOLD,
    ANALYTIC_LOW_RATING_THRESHOLD,
)
from ech.analytics.domain_events.dispatcher import DomainEventDispatcher
from ech.analytics.domain_events.events import (
    AnalyticsSnapshotCreatedEvent,
    AnalyticsSnapshotFailedEvent,
)
from ech.analytics.exceptions import (
    AnalyticsSnapshotAlreadyExistsException,
    AnalyticsSnapshotCreationException,
    IdempotencyConflictException,
)
from ech.analytics.models import (
    AnalyticsEvent,
    AnalyticsSnapshot,
    AnalyticsSnapshotLifecycle,
)
from ech.analytics.services.analytic_log_service import (
    AnalyticsLogService,
)
from ech.analytics.services.cache_service import (
    AnalyticsCacheService,
)
from ech.analytics.selectors import (
    list_customers_for_analytics,
    list_orders_for_analytics,
    list_payments_for_analytics,
    list_reviews_for_analytics,
    list_shipments_for_analytics,
    list_users_for_analytics,
)
from ech.analytics.utils.date_ranges import (
    get_period_range,
    normalize_period_bounds,
)
from ech.analytics.utils.metric_builders import (
    build_customer_metrics,
    build_empty_snapshot_metrics,
    build_order_metrics,
    build_payment_metrics,
    build_product_metrics,
    build_review_metrics,
    build_revenue_metrics,
    build_shipping_metrics,
    build_snapshot_metrics,
    build_user_metrics,
)
from ech.orders.models import Order
from ech.payments.models import Payment
from ech.reviews.models import Review
from ech.shipping.models import Shipment
from ech.users.models import CustomUser


class AnalyticsSnapshotGenerationService:
    """
    Service responsible for analytics snapshot generation.
    """

    @classmethod
    @transaction.atomic
    def generate_snapshot(
        cls,
        *,
        period_type,
        period_start=None,
        period_end=None,
        performed_by=None,
        idempotency_key=None,
        metadata=None,
    ):
        """
        Generate a new analytics snapshot for the given period.

        Args:
            period_type: Snapshot period type.
            period_start: Optional explicit period start.
            period_end: Optional explicit period end.
            performed_by: Optional user performing the action.
            idempotency_key: Optional idempotency key.
            metadata: Optional metadata payload.

        Returns:
            AnalyticsSnapshot: Created snapshot.

        Raises:
            AnalyticsSnapshotAlreadyExistsException:
                If a snapshot already exists for the given period.
            IdempotencyConflictException:
                If an idempotency key is reused for a different request.
            AnalyticsSnapshotCreationException:
                If snapshot generation fails.
        """

        resolved_period_start, resolved_period_end = cls._resolve_period_bounds(
            period_type=period_type,
            period_start=period_start,
            period_end=period_end,
        )

        existing_snapshot = cls._get_existing_snapshot_for_period(
            period_type=period_type,
            period_start=resolved_period_start,
            period_end=resolved_period_end,
        )

        if existing_snapshot:
            cls._handle_existing_snapshot(
                snapshot=existing_snapshot,
                period_type=period_type,
                period_start=resolved_period_start,
                period_end=resolved_period_end,
                idempotency_key=idempotency_key,
            )
            return existing_snapshot

        try:
            snapshot = AnalyticsSnapshot.objects.create(
                period_type=period_type,
                period_start=resolved_period_start,
                period_end=resolved_period_end,
                generated_by=performed_by,
                idempotency_key=idempotency_key,
                metadata=metadata or {},
            )

            lifecycle = AnalyticsSnapshotLifecycle.objects.create(
                snapshot=snapshot,
                generation_started_at=timezone.now(),
            )

            cls._create_event(
                snapshot=snapshot,
                event_type=AnalyticsEvent.TYPE_SNAPSHOT_GENERATION_STARTED,
                performed_by=performed_by,
                metadata=metadata,
            )

            metrics = cls._build_snapshot_metrics(
                period_start=resolved_period_start,
                period_end=resolved_period_end,
            )

            cls._apply_metrics(
                snapshot=snapshot,
                metrics=metrics,
            )

            lifecycle.generation_completed_at = timezone.now()
            lifecycle.save(
                update_fields=[
                    "generation_completed_at",
                    "updated_at",
                ]
            )

            cls._create_event(
                snapshot=snapshot,
                event_type=AnalyticsEvent.TYPE_SNAPSHOT_CREATED,
                performed_by=performed_by,
                metadata={
                    "period_type": period_type,
                    **(metadata or {}),
                },
            )

            cls._create_event(
                snapshot=snapshot,
                event_type=AnalyticsEvent.TYPE_SNAPSHOT_GENERATION_COMPLETED,
                performed_by=performed_by,
                metadata=metadata,
            )

            AnalyticsLogService.log_snapshot_created(
                snapshot=snapshot,
                performed_by=performed_by,
            )

            AnalyticsLogService.log_snapshot_metrics_updated(
                snapshot=snapshot,
                updated_fields=list(metrics.keys()),
                performed_by=performed_by,
            )

            DomainEventDispatcher.dispatch(
                AnalyticsSnapshotCreatedEvent(
                    snapshot_id=snapshot.id,
                    period_type=snapshot.period_type,
                    period_start=snapshot.period_start,
                    period_end=snapshot.period_end,
                    generated_by_id=getattr(performed_by, "id", None),
                )
            )

            transaction.on_commit(
                lambda: AnalyticsCacheService.invalidate_after_snapshot_mutation(
                    snapshot_id=snapshot.id,
                    period_type=snapshot.period_type,
                )
            )

            return snapshot

        except Exception as exc:
            DomainEventDispatcher.dispatch(
                AnalyticsSnapshotFailedEvent(
                    snapshot_id=None,
                    period_type=period_type,
                    period_start=resolved_period_start,
                    period_end=resolved_period_end,
                    error_message=str(exc),
                    performed_by_id=getattr(performed_by, "id", None),
                )
            )
            raise AnalyticsSnapshotCreationException() from exc

    @classmethod
    def _resolve_period_bounds(
        cls,
        *,
        period_type,
        period_start,
        period_end,
    ):
        """
        Resolve period bounds from explicit values or from period type.
        """

        if period_start is None and period_end is None:
            return get_period_range(period_type=period_type)

        if period_start is None or period_end is None:
            raise AnalyticsSnapshotCreationException()

        return normalize_period_bounds(
            period_start=period_start,
            period_end=period_end,
        )

    @classmethod
    def _get_existing_snapshot_for_period(
        cls,
        *,
        period_type,
        period_start,
        period_end,
    ):
        """
        Retrieve an existing snapshot for the exact same period.
        """

        return AnalyticsSnapshot.objects.filter(
            period_type=period_type,
            period_start=period_start,
            period_end=period_end,
        ).first()

    @classmethod
    def _handle_existing_snapshot(
        cls,
        *,
        snapshot,
        period_type,
        period_start,
        period_end,
        idempotency_key,
    ):
        """
        Handle an already existing snapshot for the requested period.
        """

        if idempotency_key is None:
            raise AnalyticsSnapshotAlreadyExistsException()

        if snapshot.idempotency_key == idempotency_key:
            return

        existing_by_idempotency = AnalyticsSnapshot.objects.filter(
            idempotency_key=idempotency_key,
        ).first()

        if existing_by_idempotency is None:
            raise AnalyticsSnapshotAlreadyExistsException()

        same_period_request = (
            existing_by_idempotency.period_type == period_type
            and existing_by_idempotency.period_start == period_start
            and existing_by_idempotency.period_end == period_end
        )

        if not same_period_request:
            raise IdempotencyConflictException()

    @classmethod
    def _build_snapshot_metrics(
        cls,
        *,
        period_start,
        period_end,
    ):
        """
        Build the complete analytics snapshot metrics payload.
        """

        orders = list(
            list_orders_for_analytics(
                period_start=period_start,
                period_end=period_end,
            )
        )
        payments = list(
            list_payments_for_analytics(
                period_start=period_start,
                period_end=period_end,
            )
        )
        shipments = list(
            list_shipments_for_analytics(
                period_start=period_start,
                period_end=period_end,
            )
        )
        reviews = list(
            list_reviews_for_analytics(
                period_start=period_start,
                period_end=period_end,
            )
        )
        new_customers = list(
            list_customers_for_analytics(
                period_start=period_start,
                period_end=period_end,
            )
        )
        users = list(
            list_users_for_analytics(
                period_end=period_end,
            )
        )

        if (
            not orders
            and not payments
            and not shipments
            and not reviews
            and not new_customers
            and not users
        ):
            return build_empty_snapshot_metrics()

        order_metrics = cls._build_order_metrics(orders=orders)
        revenue_metrics = cls._build_revenue_metrics(payments=payments)
        payment_metrics = cls._build_payment_metrics(payments=payments)
        shipping_metrics = cls._build_shipping_metrics(shipments=shipments)
        product_metrics = cls._build_product_metrics(orders=orders)
        customer_metrics = cls._build_customer_metrics(
            orders=orders,
            new_customers=new_customers,
        )
        user_metrics = cls._build_user_metrics(users=users)
        review_metrics = cls._build_review_metrics(reviews=reviews)

        return build_snapshot_metrics(
            order_metrics=order_metrics,
            revenue_metrics=revenue_metrics,
            payment_metrics=payment_metrics,
            shipping_metrics=shipping_metrics,
            product_metrics=product_metrics,
            customer_metrics=customer_metrics,
            user_metrics=user_metrics,
            review_metrics=review_metrics,
        )

    @classmethod
    def _build_order_metrics(cls, *, orders):
        """
        Build order metrics from order records.
        """

        return build_order_metrics(
            total_orders=len(orders),
            orders_pending=sum(
                1 for order in orders
                if order.status == Order.ORDER_STATUS_PENDING
            ),
            orders_processing=sum(
                1 for order in orders
                if order.status == Order.ORDER_STATUS_PROCESSING
            ),
            orders_shipped=sum(
                1 for order in orders
                if order.status == Order.ORDER_STATUS_SHIPPED
            ),
            orders_delivered=sum(
                1 for order in orders
                if order.status == Order.ORDER_STATUS_DELIVERED
            ),
            orders_cancelled=sum(
                1 for order in orders
                if order.status == Order.ORDER_STATUS_CANCELLED
            ),
        )

    @classmethod
    def _build_revenue_metrics(cls, *, payments):
        """
        Build revenue metrics from payment records.
        """

        total_revenue = sum(
            (
                payment.amount
                for payment in payments
                if payment.status in {
                    Payment.PAYMENT_STATUS_CAPTURED,
                    Payment.PAYMENT_STATUS_PARTIALLY_REFUNDED,
                    Payment.PAYMENT_STATUS_REFUNDED,
                }
            ),
            Decimal("0.00"),
        )

        total_refunds = sum(
            (payment.refunded_amount for payment in payments),
            Decimal("0.00"),
        )

        net_revenue = total_revenue - total_refunds

        return build_revenue_metrics(
            total_revenue=total_revenue,
            total_refunds=total_refunds,
            net_revenue=net_revenue,
        )

    @classmethod
    def _build_payment_metrics(cls, *, payments):
        """
        Build payment metrics from payment records.
        """

        return build_payment_metrics(
            payments_captured=sum(
                1 for payment in payments
                if payment.status == Payment.PAYMENT_STATUS_CAPTURED
            ),
            payments_failed=sum(
                1 for payment in payments
                if payment.status == Payment.PAYMENT_STATUS_FAILED
            ),
            payments_refunded=sum(
                1 for payment in payments
                if payment.refunded_amount > 0
            ),
        )

    @classmethod
    def _build_shipping_metrics(cls, *, shipments):
        """
        Build shipping metrics from shipment records.
        """

        return build_shipping_metrics(
            shipments_in_transit=sum(
                1 for shipment in shipments
                if shipment.status == Shipment.STATUS_IN_TRANSIT
            ),
            shipments_delivered=sum(
                1 for shipment in shipments
                if shipment.status == Shipment.STATUS_DELIVERED
            ),
            shipments_failed=sum(
                1 for shipment in shipments
                if shipment.status == Shipment.STATUS_FAILED
            ),
        )

    @classmethod
    def _build_product_metrics(cls, *, orders):
        """
        Build product metrics from order item records.
        """

        products_sold = 0
        product_quantities = {}

        for order in orders:
            for item in order.items.all():
                products_sold += item.quantity
                product_quantities[item.product_id] = (
                    product_quantities.get(item.product_id, 0) + item.quantity
                )

        top_product_id = None

        if product_quantities:
            top_product_id = max(
                product_quantities,
                key=product_quantities.get,
            )

        return build_product_metrics(
            products_sold=products_sold,
            top_product_id=top_product_id,
        )

    @classmethod
    def _build_customer_metrics(
        cls,
        *,
        orders,
        new_customers,
    ):
        """
        Build customer metrics from order and customer records.
        """

        active_customer_ids = {
            order.customer_id
            for order in orders
        }

        return build_customer_metrics(
            active_customers=len(active_customer_ids),
            new_customers=len(new_customers),
        )

    @classmethod
    def _build_user_metrics(cls, *, users):
        """
        Build user metrics from user records.
        """

        return build_user_metrics(
            total_registered_users=len(users),
            active_users=sum(
                1 for user in users
                if user.is_active
            ),
            inactive_users=sum(
                1 for user in users
                if not user.is_active
            ),
            confirmed_users=sum(
                1 for user in users
                if user.email_confirmed
            ),
            unconfirmed_users=sum(
                1 for user in users
                if not user.email_confirmed
            ),
            staff_users=sum(
                1 for user in users
                if user.user_role != CustomUser.ROLE_CUSTOMER_USER
            ),
            customer_users=sum(
                1 for user in users
                if user.user_role == CustomUser.ROLE_CUSTOMER_USER
            ),
        )

    @classmethod
    def _build_review_metrics(cls, *, reviews):
        """
        Build review metrics from review records.
        """

        total_reviews = len(reviews)

        approved_reviews = [
            review for review in reviews
            if review.status == Review.REVIEW_STATUS_APPROVED
        ]

        approved_count = len(approved_reviews)
        rejected_count = sum(
            1 for review in reviews
            if review.status == Review.REVIEW_STATUS_REJECTED
        )
        hidden_count = sum(
            1 for review in reviews
            if review.status == Review.REVIEW_STATUS_HIDDEN
        )
        cancelled_count = sum(
            1 for review in reviews
            if review.status == Review.REVIEW_STATUS_CANCELLED
        )
        verified_purchase_reviews = sum(
            1 for review in reviews
            if review.is_verified_purchase
        )

        average_rating = Decimal("0.00")
        if approved_count > 0:
            average_rating = (
                sum(
                    Decimal(str(review.rating))
                    for review in approved_reviews
                ) / approved_count
            ).quantize(Decimal("0.01"))

        product_rating_map = defaultdict(list)

        for review in approved_reviews:
            product_rating_map[review.product_id].append(review.rating)

        low_rated_products_count = 0
        high_rated_products_count = 0

        for ratings in product_rating_map.values():
            product_average = sum(ratings) / len(ratings)

            if product_average <= ANALYTIC_LOW_RATING_THRESHOLD:
                low_rated_products_count += 1

            if product_average >= ANALYTIC_HIGH_RATING_THRESHOLD:
                high_rated_products_count += 1

        return build_review_metrics(
            total_reviews=total_reviews,
            approved_reviews=approved_count,
            rejected_reviews=rejected_count,
            hidden_reviews=hidden_count,
            cancelled_reviews=cancelled_count,
            verified_purchase_reviews=verified_purchase_reviews,
            average_rating=average_rating,
            low_rated_products_count=low_rated_products_count,
            high_rated_products_count=high_rated_products_count,
        )

    @classmethod
    def _apply_metrics(
        cls,
        *,
        snapshot,
        metrics,
    ):
        """
        Apply calculated metrics to the snapshot.
        """

        update_fields = []

        for field_name, value in metrics.items():
            setattr(snapshot, field_name, value)
            update_fields.append(field_name)

        snapshot.save(update_fields=update_fields + ["updated_at"])

    @classmethod
    def _create_event(
        cls,
        *,
        snapshot,
        event_type,
        performed_by=None,
        metadata=None,
    ):
        """
        Create analytics audit event.
        """

        AnalyticsEvent.objects.create(
            snapshot=snapshot,
            event_type=event_type,
            performed_by=performed_by,
            metadata=metadata or {},
        )