from collections import defaultdict
from collections.abc import Callable
from typing import Any

from ech.payments.domain_events.events import BasePaymentDomainEvent


EventHandler = Callable[[BasePaymentDomainEvent], Any]


class PaymentDomainEventDispatcher:
    """
    In-memory dispatcher for payment domain events.

    Responsibilities:
        - register handlers by event type
        - dispatch events to all registered handlers
        - clear registered handlers when needed (mainly for tests)
    """

    def __init__(self) -> None:
        self._handlers: dict[type[BasePaymentDomainEvent], list[EventHandler]] = (
            defaultdict(list)
        )

    def register(
        self,
        event_type: type[BasePaymentDomainEvent],
        handler: EventHandler,
    ) -> None:
        """
        Register a handler for a specific event type.
        """

        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)

    def dispatch(self, event: BasePaymentDomainEvent) -> None:
        """
        Dispatch an event to all registered handlers for its exact type.
        """

        for handler in self._handlers[type(event)]:
            handler(event)

    def get_handlers(
        self,
        event_type: type[BasePaymentDomainEvent],
    ) -> list[EventHandler]:
        """
        Return all handlers registered for a given event type.
        """

        return list(self._handlers[event_type])

    def clear(self) -> None:
        """
        Remove all registered handlers.

        Mainly useful for isolated test execution.
        """

        self._handlers.clear()


payment_event_dispatcher = PaymentDomainEventDispatcher()