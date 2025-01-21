import os

from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    # label = 'main'
    name = "apps.main"

    SITE_NAME = os.environ.get("SITE_NAME")
