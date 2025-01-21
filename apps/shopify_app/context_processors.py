import shopify

from apps.shopify_app.apps import ShopifyAppConfig


def shopify_custom(request):
    _context = {}

    if not shopify.ShopifyResource.site:
        _context["current_shop"] = None
    else:
        _context["current_shop"] = shopify.ShopifyResource.site.url

    _context["shopify_app_url"] = ShopifyAppConfig.APP_URL

    return _context
