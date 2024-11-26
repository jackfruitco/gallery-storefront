from django.apps import apps

def get_store_url(request=None):
    return apps.get_app_config('store').store_url