import shopify

from .apps import ShopifyAppConfig


class ConfigurationError(BaseException):
    pass


class LoginProtection(object):
    def __init__(self, get_response):
        self.get_response = get_response
        self.api_key = ShopifyAppConfig.API_KEY
        self.api_secret = ShopifyAppConfig.API_SECRET
        if not self.api_key or not self.api_secret:
            raise ConfigurationError(
                "API_KEY and API_SECRET must be set in ShopifyAppConfig"
            )
        shopify.Session.setup(api_key=self.api_key, secret=self.api_secret)

    def __call__(self, request):
        if hasattr(request, "session") and "shopify" in request.session:
            api_version = ShopifyAppConfig.API_VERSION
            shop_url = request.session["shopify"]["shop_url"]
            shopify_session = shopify.Session(shop_url, api_version)
            shopify_session.token = request.session["shopify"]["access_token"]
            shopify.ShopifyResource.activate_session(shopify_session)
        response = self.get_response(request)
        shopify.ShopifyResource.clear_session()
        return response
