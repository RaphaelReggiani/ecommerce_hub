from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ech.products"

    def ready(self):
        from ech.products.domain_events import registry