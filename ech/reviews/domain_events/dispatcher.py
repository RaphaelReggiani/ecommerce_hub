from collections import defaultdict
from typing import Callable


class ReviewEventDispatcher:
    """
    In-memory dispatcher for reviews domain events.
    """

    _handlers: dict[type, list[Callable]] = defaultdict(list)

    @classmethod
    def register(cls, event_type, handler):
        if handler not in cls._handlers[event_type]:
            cls._handlers[event_type].append(handler)

    @classmethod
    def dispatch(cls, event):
        handlers = cls._handlers.get(type(event), [])

        for handler in handlers:
            handler(event)

    @classmethod
    def clear(cls):
        cls._handlers.clear()