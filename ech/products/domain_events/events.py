from dataclasses import dataclass


@dataclass(frozen=True)
class ProductCreatedEvent:
    product: object
    performed_by: object


@dataclass(frozen=True)
class ProductUpdatedEvent:
    product: object
    performed_by: object


@dataclass(frozen=True)
class ProductDeletedEvent:
    product: object
    performed_by: object
    reason: str = "manual_deletion"


@dataclass(frozen=True)
class ProductImageUploadedEvent:
    product: object
    performed_by: object