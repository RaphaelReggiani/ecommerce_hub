from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import uuid

from django.utils import timezone


@dataclass(frozen=True)
class BaseReviewDomainEvent:
    """
    Base domain event for the reviews module.
    """

    review_id: uuid.UUID
    occurred_at: datetime = field(default_factory=timezone.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ReviewCreatedEvent(BaseReviewDomainEvent):
    pass


@dataclass(frozen=True)
class ReviewUpdatedEvent(BaseReviewDomainEvent):
    pass


@dataclass(frozen=True)
class ReviewApprovedEvent(BaseReviewDomainEvent):
    pass


@dataclass(frozen=True)
class ReviewRejectedEvent(BaseReviewDomainEvent):
    pass


@dataclass(frozen=True)
class ReviewHiddenEvent(BaseReviewDomainEvent):
    pass


@dataclass(frozen=True)
class ReviewRestoredEvent(BaseReviewDomainEvent):
    pass


@dataclass(frozen=True)
class ReviewCancelledEvent(BaseReviewDomainEvent):
    pass