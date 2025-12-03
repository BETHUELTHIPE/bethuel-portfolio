from django.apps import AppConfig


class ResumeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "resume"

    def ready(self):  # pragma: no cover - import signals for side effects
        from . import signals  # noqa: F401
