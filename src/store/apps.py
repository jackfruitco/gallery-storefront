import os

from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "store"

    storefront_url = os.getenv("STOREFRONT_URL")
