from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.apps import apps
from .models import ShopifyAccessToken
import binascii, os, shopify
from django.contrib.admin.views.decorators import staff_member_required

shop_url = apps.get_app_config('shopify_app').SHOPIFY_URL
api_version = apps.get_app_config('shopify_app').SHOPIFY_API_VERSION

def _new_session():
    return shopify.Session(shop_url, api_version)


@staff_member_required
def login(request):
    # If the ${shop}.myshopify.com address is already provided in the URL,
    # just skip to authenticate
    if shop_url:
        return authenticate(request)
    return render(request, 'shopify_app/login.html', {})


def authenticate(request):
    if not shop_url:
        messages.error(request, "A shop param is required")
        return redirect(reverse(login))
    scope = apps.get_app_config('shopify_app').SHOPIFY_API_SCOPES
    redirect_uri = request.build_absolute_uri(reverse('shopify:finalize'))
    state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")

    auth_url = _new_session().create_permission_url(scope, redirect_uri, state)
    return redirect(auth_url)


def finalize(request):
    shop_url = apps.get_app_config('shopify_app').SHOPIFY_URL
    session = shopify.Session(shop_url, api_version)
    params = request.GET.dict()
    access_token = session.request_token(params)

    # Update (or create) access_token in user profile
    obj, created = ShopifyAccessToken.objects.update_or_create(
        user=request.user,
        defaults={"user": request.user,
                  "access_token": access_token },
    )

    session = shopify.Session(shop_url, api_version, access_token)
    shopify.ShopifyResource.activate_session(session)

    # try:
    #     shop_url = params['shop']
    #     session = _new_session()
    #     request.session['shopify'] = {
    #         "shop_url": shop_url,
    #         "access_token": session.request_token(request.GET)
    #     }
    # except Exception:
    #     messages.error(request, "Could not log in to Shopify store.")
    #     return redirect(reverse(login))
    # messages.info(request, "Logged in to shopify store.")
    # request.session.pop('return_to', None)
    return redirect(request.session.get('return_to', reverse('admin:index')))

def logout(request):
    request.session.pop('shopify', None)
    messages.info(request, "Successfully logged out.")
    return redirect(reverse(login))

def sync_error(request):
    return render(request, "shopify_app/sync-error.html")

def sync_success(request):
    return render(request, "shopify_app/sync-debug.html")