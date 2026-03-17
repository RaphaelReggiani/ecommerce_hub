class EventDispatcher:
    _handlers = {}

    @classmethod
    def register(cls, event_type, handler):
        cls._handlers.setdefault(event_type, []).append(handler)

    @classmethod
    def dispatch(cls, event):
        handlers = cls._handlers.get(type(event), [])

        for handler in handlers:
            handler(event)

    @classmethod
    def clear(cls):
        cls._handlers = {}