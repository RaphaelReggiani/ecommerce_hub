from decimal import Decimal

from ech.analytics.exceptions import (
    AnalyticsPaymentUnavailableException,
)
from ech.analytics.selectors import (
    get_latest_analytics_snapshot_by_period_type,
    list_payments_for_analytics,
)
from ech.analytics.services.analytic_log_service import (
    AnalyticsLogService,
)
from ech.analytics.services.cache_service import (
    AnalyticsCacheService,
)
from ech.analytics.utils.cache_keys import (
    payment_overview_cache_key,
)
from ech.analytics.utils.date_ranges import (
    get_period_range,
)
from ech.payments.models import Payment


class AnalyticsPaymentOverviewService:
    """
    Service responsible for payment analytics overview data.
    """

    @classmethod
    def get_overview(
        cls,
        *,
        period_type,
        period_start=None,
        period_end=None,
        performed_by=None,
    ):
        """
        Retrieve payment analytics overview for the requested period.

        Snapshot data is preferred when the latest snapshot matches the
        requested bounds. Otherwise, metrics are calculated in real time.
        """

        resolved_period_start, resolved_period_end = cls._resolve_period_bounds(
            period_type=period_type,
            period_start=period_start,
            period_end=period_end,
        )

        payment_version = AnalyticsCacheService.get_payment_version()
        cache_key = payment_overview_cache_key(
            period_start=resolved_period_start,
            period_end=resolved_period_end,
            payment_version=payment_version,
        )

        def producer():
            snapshot = cls._get_matching_snapshot(
                period_type=period_type,
                period_start=resolved_period_start,
                period_end=resolved_period_end,
            )

            if snapshot is not None:
                payload = cls._build_overview_from_snapshot(snapshot=snapshot)
            else:
                payload = cls._build_overview_realtime(
                    period_start=resolved_period_start,
                    period_end=resolved_period_end,
                )

            AnalyticsLogService.log_payment_metrics_calculated(
                period_start=resolved_period_start,
                period_end=resolved_period_end,
                captured_payments=payload["captured_payments"],
                failed_payments=payload["failed_payments"],
                refunded_payments=payload["refunded_payments"],
                performed_by=performed_by,
            )

            return payload

        try:
            return AnalyticsCacheService.get_or_set(
                key=cache_key,
                producer=producer,
                timeout=None,
            )
        except Exception as exc:
            raise AnalyticsPaymentUnavailableException() from exc

    @classmethod
    def _resolve_period_bounds(
        cls,
        *,
        period_type,
        period_start,
        period_end,
    ):
        """
        Resolve payment overview period bounds.
        """

        if period_start is None and period_end is None:
            return get_period_range(period_type=period_type)

        if period_start is None or period_end is None:
            raise AnalyticsPaymentUnavailableException()

        return period_start, period_end

    @classmethod
    def _get_matching_snapshot(
        cls,
        *,
        period_type,
        period_start,
        period_end,
    ):
        """
        Return the latest snapshot only if it matches the requested period.
        """

        try:
            snapshot = get_latest_analytics_snapshot_by_period_type(
                period_type=period_type,
            )
        except Exception:
            return None

        if (
            snapshot.period_start == period_start
            and snapshot.period_end == period_end
        ):
            return snapshot

        return None

    @classmethod
    def _build_overview_from_snapshot(cls, *, snapshot):
        """
        Build payment overview payload from a materialized snapshot.
        """

        total_payment_operations = (
            snapshot.payments_captured
            + snapshot.payments_failed
            + snapshot.payments_refunded
        )

        capture_rate = 0
        failure_rate = 0
        refund_rate = 0

        if total_payment_operations > 0:
            capture_rate = snapshot.payments_captured / total_payment_operations
            failure_rate = snapshot.payments_failed / total_payment_operations
            refund_rate = snapshot.payments_refunded / total_payment_operations

        return {
            "source": "snapshot",
            "snapshot_id": snapshot.id,
            "period_type": snapshot.period_type,
            "period_start": snapshot.period_start,
            "period_end": snapshot.period_end,
            "captured_payments": snapshot.payments_captured,
            "failed_payments": snapshot.payments_failed,
            "refunded_payments": snapshot.payments_refunded,
            "total_refunded_amount": snapshot.total_refunds,
            "net_revenue": snapshot.net_revenue,
            "capture_rate": capture_rate,
            "failure_rate": failure_rate,
            "refund_rate": refund_rate,
        }

    @classmethod
    def _build_overview_realtime(
        cls,
        *,
        period_start,
        period_end,
    ):
        """
        Build payment overview in real time from payment records.
        """

        payments = list(
            list_payments_for_analytics(
                period_start=period_start,
                period_end=period_end,
            )
        )

        captured_payments = sum(
            1 for payment in payments
            if payment.status == Payment.PAYMENT_STATUS_CAPTURED
        )

        failed_payments = sum(
            1 for payment in payments
            if payment.status == Payment.PAYMENT_STATUS_FAILED
        )

        refunded_payments = sum(
            1 for payment in payments
            if payment.refunded_amount > 0
        )

        total_refunded_amount = sum(
            (payment.refunded_amount for payment in payments),
            Decimal("0.00"),
        )

        total_captured_amount = sum(
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

        net_revenue = total_captured_amount - total_refunded_amount

        total_payment_operations = (
            captured_payments
            + failed_payments
            + refunded_payments
        )

        capture_rate = 0
        failure_rate = 0
        refund_rate = 0

        if total_payment_operations > 0:
            capture_rate = captured_payments / total_payment_operations
            failure_rate = failed_payments / total_payment_operations
            refund_rate = refunded_payments / total_payment_operations

        return {
            "source": "realtime",
            "snapshot_id": None,
            "period_type": None,
            "period_start": period_start,
            "period_end": period_end,
            "captured_payments": captured_payments,
            "failed_payments": failed_payments,
            "refunded_payments": refunded_payments,
            "total_refunded_amount": total_refunded_amount,
            "net_revenue": net_revenue,
            "capture_rate": capture_rate,
            "failure_rate": failure_rate,
            "refund_rate": refund_rate,
        }