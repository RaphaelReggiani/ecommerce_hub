from datetime import datetime, time, timedelta

from django.utils import timezone

from ech.analytics.models import AnalyticsSnapshot


def get_current_time():
    """
    Return the current timezone-aware datetime.
    """
    return timezone.now()


def get_day_range(*, reference_datetime=None):
    """
    Return the start and end datetimes for the day
    containing the given reference datetime.
    """

    if reference_datetime is None:
        reference_datetime = get_current_time()

    local_datetime = timezone.localtime(reference_datetime)

    start = local_datetime.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    end = start + timedelta(days=1)

    return start, end


def get_week_range(*, reference_datetime=None):
    """
    Return the start and end datetimes for the week
    containing the given reference datetime.

    Week starts on Monday.
    """

    if reference_datetime is None:
        reference_datetime = get_current_time()

    local_datetime = timezone.localtime(reference_datetime)

    start_of_day = local_datetime.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    start = start_of_day - timedelta(days=start_of_day.weekday())
    end = start + timedelta(days=7)

    return start, end


def get_month_range(*, reference_datetime=None):
    """
    Return the start and end datetimes for the month
    containing the given reference datetime.
    """

    if reference_datetime is None:
        reference_datetime = get_current_time()

    local_datetime = timezone.localtime(reference_datetime)

    start = local_datetime.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    if start.month == 12:
        end = start.replace(
            year=start.year + 1,
            month=1,
        )
    else:
        end = start.replace(
            month=start.month + 1,
        )

    return start, end


def get_period_range(*, period_type, reference_datetime=None):
    """
    Return the period start and end datetimes
    based on the analytics snapshot period type.
    """

    if period_type == AnalyticsSnapshot.PERIOD_DAILY:
        return get_day_range(reference_datetime=reference_datetime)

    if period_type == AnalyticsSnapshot.PERIOD_WEEKLY:
        return get_week_range(reference_datetime=reference_datetime)

    if period_type == AnalyticsSnapshot.PERIOD_MONTHLY:
        return get_month_range(reference_datetime=reference_datetime)

    raise ValueError(f"Unsupported period type: {period_type}")


def normalize_period_bounds(*, period_start, period_end):
    """
    Normalize custom period bounds to timezone-aware datetimes.

    Supports date or datetime inputs.
    """

    if isinstance(period_start, datetime):
        normalized_start = period_start
    else:
        normalized_start = datetime.combine(period_start, time.min)

    if isinstance(period_end, datetime):
        normalized_end = period_end
    else:
        normalized_end = datetime.combine(period_end, time.min)

    if timezone.is_naive(normalized_start):
        normalized_start = timezone.make_aware(
            normalized_start,
            timezone.get_current_timezone(),
        )

    if timezone.is_naive(normalized_end):
        normalized_end = timezone.make_aware(
            normalized_end,
            timezone.get_current_timezone(),
        )

    return normalized_start, normalized_end


def get_previous_period_range(*, period_start, period_end):
    """
    Return the immediately previous period range
    with the same duration as the given range.
    """

    duration = period_end - period_start
    previous_end = period_start
    previous_start = previous_end - duration

    return previous_start, previous_end