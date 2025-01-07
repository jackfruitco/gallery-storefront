import shopify
import os

def shopify_context(request):
    _context = {}

    if not shopify.ShopifyResource.site:
        _context['current_shop'] =  None
    else: _context['current_shop'] = shopify.ShopifyResource.site.url

    _context['storefront_url'] = os.getenv('STOREFRONT_URL')
    return _context