from django.apps import AppConfig


class MembersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.members"

    def ready(self) -> None:
        from . import signals  # noqa: F401
