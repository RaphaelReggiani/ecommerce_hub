from ech.shipping.domain_events.registry import (
    EVENT_HANDLER_REGISTRY,
)


class DomainEventDispatcher:
    """
    Dispatches domain events to all registered handlers.
    """

    @staticmethod
    def dispatch(event):
        """
        Dispatch an event to all handlers registered for its class.
        """

        handlers = EVENT_HANDLER_REGISTRY.get(type(event), [])

        for handler in handlers:
            handler(event)