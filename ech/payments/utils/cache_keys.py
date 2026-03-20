from uuid import UUID


class PaymentCacheKeys:
    """
    Centralized cache key builder for payments domain.

    This class standardizes cache key generation to ensure:
        - consistency across the application
        - easier cache invalidation
        - no hardcoded keys scattered across services
    """

    PREFIX = "payments"

    @classmethod
    def payment_detail(cls, payment_id: UUID) -> str:
        return f"{cls.PREFIX}:payment:{payment_id}"

    @classmethod
    def payment_by_reference(cls, payment_reference: str) -> str:
        return f"{cls.PREFIX}:payment:ref:{payment_reference}"

    @classmethod
    def customer_payments(cls, customer_id: UUID, page: int = 1) -> str:
        return f"{cls.PREFIX}:customer:{customer_id}:payments:page:{page}"

    @classmethod
    def payments_by_status(cls, status: str, page: int = 1) -> str:
        return f"{cls.PREFIX}:payments:status:{status}:page:{page}"

    @classmethod
    def payments_by_method(cls, method: str, page: int = 1) -> str:
        return f"{cls.PREFIX}:payments:method:{method}:page:{page}"

    @classmethod
    def management_payments(cls, page: int = 1) -> str:
        return f"{cls.PREFIX}:management:payments:page:{page}"

    @classmethod
    def payment_transactions(cls, payment_id: UUID) -> str:
        return f"{cls.PREFIX}:payment:{payment_id}:transactions"

    @classmethod
    def payment_refunds(cls, payment_id: UUID) -> str:
        return f"{cls.PREFIX}:payment:{payment_id}:refunds"

    @classmethod
    def payment_pattern(cls, payment_id: UUID) -> str:
        """
        Pattern used for bulk invalidation of a payment and its related data.
        """

        return f"{cls.PREFIX}:payment:{payment_id}*"

    @classmethod
    def customer_pattern(cls, customer_id: UUID) -> str:
        return f"{cls.PREFIX}:customer:{customer_id}*"

    @classmethod
    def global_payments_pattern(cls) -> str:
        return f"{cls.PREFIX}:payments:*"

    @classmethod
    def management_pattern(cls) -> str:
        return f"{cls.PREFIX}:management:*"