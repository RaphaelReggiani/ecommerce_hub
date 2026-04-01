from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ech.products"

    def ready(self):
        """
        Registers product domain event handlers on app startup.
        """

        from ech.products.domain_events.registry import (
            register_product_event_handlers,
        )

        register_product_event_handlers()
