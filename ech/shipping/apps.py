from django.apps import AppConfig


class ShippingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ech.shipping"

    def ready(self):
        from ech.shipping.domain_events import registry

