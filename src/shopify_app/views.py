import logging
import os

import binascii
import shopify
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from six.moves import urllib

from .apps import ShopifyAppConfig
from .models import ShopifyAccessToken

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

SHOP_URL = ShopifyAppConfig.SHOP_DOMAIN
API_VERSION = ShopifyAppConfig.API_VERSION


def _new_session():
    return shopify.Session(SHOP_URL, API_VERSION)


@staff_member_required
def login(request):
    # If the ${shop}.myshopify.com address is already provided in the URL,
    # just skip to authenticate
    if SHOP_URL:
        logger.info("shop_url already exists: %s" % SHOP_URL)
        return authenticate(request)
    return render(request, "shopify_app/login.html", {})


def authenticate(request):
    if not SHOP_URL:
        messages.error(request, "A shop param is required")
        return redirect(reverse("shopify:login"))

    redirect_uri = request.build_absolute_uri(reverse("shopify:finalize"))
    state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")

    # auth_url = _new_session().create_permission_url(scope, redirect_uri, state)
    session = _new_session()
    query_params = dict(client_id=session.api_key, redirect_uri=redirect_uri)
    if state:
        query_params["state"] = state
    auth_url = "https://%s/admin/oauth/authorize?%s" % (
        session.url,
        urllib.parse.urlencode(query_params),
    )

    logger.debug("auth_url finished: %s" % auth_url)
    return redirect(auth_url)


def finalize(request):
    session = shopify.Session(SHOP_URL, API_VERSION)
    params = request.GET.dict()
    logger.debug("Shopify Auth Response Params: %s" % params)

    access_token = session.request_token(params)

    # Update (or create) access_token in user profile
    obj, created = ShopifyAccessToken.objects.update_or_create(
        user=request.user,
        defaults={"user": request.user, "access_token": access_token, "shop": SHOP_URL},
    )

    logger.info(
        "ShopifyAccessToken saved (store: %s; user: %s)" % (SHOP_URL, request.user)
    )
    messages.success(
        request,
        "ShopifyAccessToken saved! You can now sync items with the Shopify storefront.",
    )

    session = shopify.Session(SHOP_URL, API_VERSION, access_token)
    shopify.ShopifyResource.activate_session(session)

    return redirect(request.session.get("return_to", reverse("admin:index")))


def logout(request):
    request.session.pop("shopify", None)
    messages.info(request, "Successfully logged out.")
    return redirect(reverse(login))
