from os.path import exists

from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from apps.shopify_app.models import ShopifyAccessToken
import logging
from django.conf import settings
from . import views

logger = logging.getLogger(__name__)

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
        logger.debug("@shopify_token_required decorator called")
        if not ShopifyAccessToken.objects.filter(user=1).exists():
            logger.debug("Token does not exist")
            # messages.error(, "Unable to complete Shopify Sync: Token does not exist")
            return redirect(reverse('shopify:login'))
        return fn(request, *args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

