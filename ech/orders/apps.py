from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ech.orders"

    def ready(self):
        from ech.orders.domain_events.registry import register_order_event_handlers
        register_order_event_handlers()
