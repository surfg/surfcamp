from django.apps import AppConfig


class CampsConfig(AppConfig):
    name = 'camps'

    def ready(self):
        from . import signals  # noqa: F401
