import os
from datetime import datetime

from django.apps import AppConfig


def get_current_api_version() -> str:
    """
    Return the current API version based on the current month.

    This function calculates the current API version formatted as `<year>-<month>`,
    where `<month>` is one of the predefined API release versions: '01', '04', '07',
    or '10', offset by 30d off the current month. Specifically:
    - '01' corresponds to February through April,
    - '04' corresponds to May through July,
    - '07' corresponds to August through October,
    - '10' corresponds to November through January.

    :raises ValueError: If the current month cannot be matched to a valid API release
                        version.
    :return: A string representing the API version in the format `<year>-<month>`.
    :rtype: str
    """
    _today = datetime.today()
    match _today.month:
        case 2 | 3 | 4: _month = '01'
        case 5 | 6 | 7: _month = '04'
        case 8 | 9 | 10: _month = '07'
        case 11 | 12 | 1: _month = '10'
        case _: raise ValueError('Invalid month')
    return '%s-%s' % (_today.year, _month)

class ShopifyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.shopify_app'

    API_KEY = os.environ.get('SHOPIFY_API_KEY')
    API_SECRET = os.environ.get('SHOPIFY_API_SECRET')

    API_VERSION = os.environ.get('SHOPIFY_API_VERSION',
                                 get_current_api_version())

    SHOP_DOMAIN = os.environ.get('SHOPIFY_DOMAIN')
    ADMIN_URL = 'https://admin.shopify.com/store/%s' % SHOP_DOMAIN

    # URL for Online Store homepage
    APP_URL = os.environ.get(
        'SHOPIFY_APP_URL',
        'https://%s.myshopify.com' % SHOP_DOMAIN
    )

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
