from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ech.analytics"

    def ready(self):
        """
        Import analytics domain event registry on app startup
        so event-handler mappings are loaded.
        """
        from ech.analytics.domain_events import registry