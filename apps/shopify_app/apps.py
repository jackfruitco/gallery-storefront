import os

from django.apps import AppConfig


class ShopifyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.shopify_app'

    API_KEY = os.environ.get('API_KEY')
    API_SECRET = os.environ.get('API_SECRET')
    SHOP_URL = os.environ.get('SHOP_URL')
    API_VERSION = os.environ.get('API_VERSION', '2024-07')
    MAIN_LOCATION = os.environ.get('SHOPIFY_MAIN_LOCATION')

    SHOPIFY_PUBLICATIONS = [
        {
            "name": "Online Store",
            "id": os.environ.get('SHOPIFY_ONLINE_PUB_ID'),
        },
        {
            "name": "POS",
            "id": os.environ.get('SHOPIFY_POS_PUB_ID'),
        }
    ]

    # def ready(self):
    #    import apps.shopify_app.signals
