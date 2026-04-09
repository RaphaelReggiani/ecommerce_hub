from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ech.payments"

    def ready(self):
        """
        Ensure domain event registry is loaded when the app starts.
        """
        from ech.payments.domain_events import registry