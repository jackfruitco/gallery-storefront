from os.path import exists

from django.shortcuts import redirect
from django.urls import reverse
from apps.shopify_app.models import ShopifyAccessToken
from django.conf import settings
from . import views

def shop_login_required(fn):
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'session') or 'shopify' not in request.session:
            #request.session['return_to'] = request.get_full_path()
            request.session['return_to'] = reverse('admin')
            return redirect(reverse('shopify:login'))
        return fn(request, *args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

def shopify_token_required(fn):
    def wrapper(request, *args, **kwargs):
        if not ShopifyAccessToken.objects.filter(user=1).exists():
            return redirect(reverse('shopify:login'))
        return fn(request, *args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

