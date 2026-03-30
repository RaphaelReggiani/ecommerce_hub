from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ech.reviews"

    def ready(self):
        from ech.reviews.domain_events.registry import (
            register_review_event_handlers,
        )

        register_review_event_handlers()