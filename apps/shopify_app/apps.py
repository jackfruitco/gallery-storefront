from django.apps import AppConfig
import os

class ShopifyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.shopify_app'

    SHOPIFY_API_KEY = os.environ.get('SHOPIFY_API_KEY')
    SHOPIFY_API_SECRET = os.environ.get('SHOPIFY_API_SECRET')
    SHOPIFY_API_URL = os.environ.get('SHOPIFY_API_URL')
    SHOPIFY_API_VERSION = os.environ.get('SHOPIFY_API_VERSION', '2024-07')
    SHOPIFY_API_SCOPES = os.environ.get('SHOPIFY_API_SCOPES', 'read_products,read_orders').split(',')