from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ech.notifications"

    def ready(self):
        """
        Import notification domain event registry on app startup
        so event-handler mappings are loaded.
        """
        from ech.notifications.domain_events import registry