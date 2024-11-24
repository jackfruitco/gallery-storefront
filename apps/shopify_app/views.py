import binascii
import logging
import os
import shopify

from django.apps import apps
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.urls import reverse
from six.moves import urllib

from .models import ShopifyAccessToken

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

shop_url = apps.get_app_config('shopify_app').SHOPIFY_URL
api_version = apps.get_app_config('shopify_app').SHOPIFY_API_VERSION

def _new_session():
    return shopify.Session(shop_url, api_version)


@staff_member_required
def login(request):
    # If the ${shop}.myshopify.com address is already provided in the URL,
    # just skip to authenticate
    if shop_url:
        logger.info('shop_url already exists: %s' % shop_url)
        return authenticate(request)
    return render(request, 'shopify_app/login.html', {})


def authenticate(request):
    if not shop_url:
        messages.error(request, "A shop param is required")
        return redirect(reverse(login))
    # scope = apps.get_app_config('shopify_app').SHOPIFY_API_SCOPES
    redirect_uri = request.build_absolute_uri(reverse('shopify:finalize'))
    state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")

    # auth_url = _new_session().create_permission_url(scope, redirect_uri, state)
    session = _new_session()
    query_params = dict(client_id=session.api_key, redirect_uri=redirect_uri)
    if state:
        query_params["state"] = state
    auth_url = "https://%s/admin/oauth/authorize?%s" % (session.url, urllib.parse.urlencode(query_params))

    logger.debug('auth_url finished: %s' % auth_url)
    return redirect(auth_url)


def finalize(request):
    shop_url = apps.get_app_config('shopify_app').SHOPIFY_URL
    session = shopify.Session(shop_url, api_version)
    params = request.GET.dict()
    logger.debug("Shopify Auth Response Params: %s" % params)

    access_token = session.request_token(params)

    # Update (or create) access_token in user profile
    obj, created = ShopifyAccessToken.objects.update_or_create(
        user=request.user,
        defaults={"user": request.user,
                  "access_token": access_token,
                  "shop": shop_url},
    )

    logger.info("ShopifyAccessToken saved (store: %s; user: %s)" % (shop_url, request.user) )
    messages.success(request, "ShopifyAccessToken saved! You can now sync items with the Shopify storefront.")

    session = shopify.Session(shop_url, api_version, access_token)
    shopify.ShopifyResource.activate_session(session)

    return redirect(request.session.get('return_to', reverse('admin:index')))

def logout(request):
    request.session.pop('shopify', None)
    messages.info(request, "Successfully logged out.")
    return redirect(reverse(login))

def sync_error(request):
    return render(request, "shopify_app/sync-error.html")

def sync_success(request):
    return render(request, "shopify_app/sync-debug.html")