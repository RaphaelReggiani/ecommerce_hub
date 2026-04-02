from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ech.users"

    def ready(self):
        """
        Ensure domain event registry is loaded when the app starts.
        """

        import ech.users.domain_events.registry