from django.apps import AppConfig


class AdminDashboardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ech.admin_dashboard"

    def ready(self):
        """
        Import admin dashboard domain event registry during app startup
        so event-handler mappings are registered.

        This ensures that all domain events dispatched within the
        admin_dashboard module are properly handled.
        """

        from ech.admin_dashboard.domain_events import registry as _registry