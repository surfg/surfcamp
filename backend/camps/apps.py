from django.apps import AppConfig


class CampsConfig(AppConfig):
    name = 'camps'

    def ready(self):
        # Enable HEIC/HEIF (iPhone default format) support in Pillow.
        try:
            from pillow_heif import register_heif_opener
            register_heif_opener()
        except ImportError:
            pass

        from . import signals  # noqa: F401
