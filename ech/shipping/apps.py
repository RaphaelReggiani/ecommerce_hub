from django.apps import AppConfig


class ShippingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ech.shipping"

    # def ready(self):
    #     from ech.shipping.domain_events.registry import register_shipping_event_handlers
    #     register_shipping_event_handlers()
