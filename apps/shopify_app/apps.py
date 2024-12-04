from django.apps import AppConfig
import os, shopify

class ShopifyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.shopify_app'

    SHOPIFY_API_KEY = os.environ.get('SHOPIFY_API_KEY')
    SHOPIFY_API_SECRET = os.environ.get('SHOPIFY_API_SECRET')
    SHOPIFY_URL = os.environ.get('SHOPIFY_URL')
    SHOPIFY_API_VERSION = os.environ.get('SHOPIFY_API_VERSION', '2024-07')
    MAIN_LOCATION = os.environ.get('SHOPIFY_MAIN_LOCATION')
    SHOPIFY_ACCESS_TOKEN = None

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

    def ready(self):
        import apps.shopify_app.signals
