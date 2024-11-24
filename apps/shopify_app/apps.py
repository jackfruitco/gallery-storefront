from django.apps import AppConfig
import os, shopify

class ShopifyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.shopify_app'

    SHOPIFY_API_KEY = os.environ.get('SHOPIFY_API_KEY')
    SHOPIFY_API_SECRET = os.environ.get('SHOPIFY_API_SECRET')
    SHOPIFY_URL = os.environ.get('SHOPIFY_URL')
    SHOPIFY_API_VERSION = os.environ.get('SHOPIFY_API_VERSION', '2024-07')
    SHOPIFY_API_SCOPES = os.environ.get('SHOPIFY_API_SCOPES', 'read_products,read_orders').split(',')
    SHOPIFY_ACCESS_TOKEN = None

    SHOPIFY_PUBLICATIONS = [
        {
            "name": "Online Store",
            "gid": os.environ.get('SHOPIFY_ONLINE_PUB_ID'),
        },
        {
            "name": "POS",
            "gid": os.environ.get('SHOPIFY_POS_PUB_ID'),
        }
    ]

    SHOPIFY_ONLINE_PUB_ID = os.environ.get('SHOPIFY_ONLINE_PUB_ID')
    SHOPIFY_POS_PUB_ID = os.environ.get('SHOPIFY_POS_PUB_ID')

    def store_access_token(self, access_token):
        self.SHOPIFY_ACCESS_TOKEN = access_token
        return self

