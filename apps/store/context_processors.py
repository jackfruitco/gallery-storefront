from django.apps import apps

def store_url(request=None):
    return {
        "storefront_url": apps.get_app_config('store').storefront_url,
    }

def locations(request=None):
    return {
        "main": apps.get_app_config('shopify_app').MAIN_LOCATION,
    }