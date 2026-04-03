from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ech.notifications"

    # def ready(self):
    #     from ech.notifications.domain_events.registry import (
    #         register_notification_event_handlers,
    #     )

    #     register_notification_event_handlers()