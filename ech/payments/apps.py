from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ech.payments"

    def ready(self):
        from ech.payments.domain_events.registry import register_payment_event_handlers

        register_payment_event_handlers()