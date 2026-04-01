class EventDispatcher:
    """
    Simple synchronous domain event dispatcher.

    Each event type can have multiple handlers registered.
    When an event is dispatched, all registered handlers
    for that event type are executed sequentially.
    """

    _handlers = {}

    @classmethod
    def register(cls, event_type, handler):
        """
        Registers a handler for a given event type.
        """
        cls._handlers.setdefault(event_type, []).append(handler)

    @classmethod
    def dispatch(cls, event):
        """
        Dispatches an event to all registered handlers.
        """
        handlers = cls._handlers.get(type(event), [])

        for handler in handlers:
            try:
                handler(event)
            except Exception:

                continue

    @classmethod
    def clear(cls):
        """
        Clears all registered handlers.
        Useful mainly for tests.
        """
        cls._handlers = {}