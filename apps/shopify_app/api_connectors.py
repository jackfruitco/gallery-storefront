from apps.shopify_app.decorators import shopify_token_required
from apps.shopify_app.models import ShopifyAccessToken
from django.apps import apps
from django.utils.text import slugify
import json, shopify, logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@shopify_token_required
def _shop_sync(self):
    """Sync product with Shopify"""
    shop_url = apps.get_app_config('shopify_app').SHOPIFY_URL
    api_version = apps.get_app_config('shopify_app').SHOPIFY_API_VERSION

    # ! BUG: add error handling for when token does not exist. Consider shop login decorator
    # ! BUG: get access_token for user logged in
    token = ShopifyAccessToken.objects.get(user=1).access_token
    document = open('/app/apps/shopify_app/product_mutations.graphql', 'r').read()

    with shopify.Session.temp(shop_url, api_version, token):
        if self.shop_GID:
            response = shopify.GraphQL().execute(
                query=document,
                variables={
                    "synchronous": True,
                    "productSet": {
                        "title": self.name,
                        "descriptionHtml": "<p>%s</p>" % self.description,
                        "id": self.shop_GID,
                        "handle": slugify(self.name),
                        # "productType": self.category.name,
                        "status": self.shop_status,
                        "productOptions": [
                            {
                                "name": "Color",
                                "position": 1,
                                "values": [
                                    {"name": self.primary_color.name},
                                ]
                            }
                        ],
                        "variants": [
                            {
                                "optionValues": [{
                                    "optionName": "Color",
                                    "name": self.primary_color.name,
                                }],
                                "price": self.price,
                            },
                        ],
                    }
                },
                operation_name='createProductSynchronous',
            )
        else:
            response = shopify.GraphQL().execute(
                query=document,
                variables={
                    "synchronous": True,
                    "productSet": {
                        "title": self.name,
                        "descriptionHtml": "<p>%s</p>" % self.description,
                        # "id": self.shop_GID,
                        "handle": slugify(self.name),
                        # "productType": self.category.name,
                        "status": self.shop_status,
                        "productOptions": [
                            {
                                "name": "Color",
                                "position": 1,
                                "values": [
                                    {"name": self.primary_color.name},
                                ]
                            }
                        ],
                        "variants": [
                            {
                                "optionValues": [{
                                    "optionName": "Color",
                                    "name": self.primary_color.name,
                                }],
                                "price": self.price,
                            },
                        ],
                    }
                },
                operation_name='createProductSynchronous',
            )

    logger.warning(json.loads(response)['data']['productSet']['product']['id'])

    return response

@shopify_token_required
def _shop_publish(productID):
    shop_url = apps.get_app_config('shopify_app').SHOPIFY_URL
    api_version = apps.get_app_config('shopify_app').SHOPIFY_API_VERSION

    # ! BUG: add error handling for when token does not exist. Consider shop login decorator
    # ! BUG: get access_token for user logged in
    token = ShopifyAccessToken.objects.get(user=1).access_token
    document = open('/app/apps/shopify_app/product_mutations.graphql', 'r').read()

    with shopify.Session.temp(shop_url, api_version, token):
        response = shopify.GraphQL().execute(
            query=document,
            variables={
                "id": productID,
                "input": {
                    "publicationId": "gid://shopify/Publication/148057129196"
                }
            },
            operation_name='publishablePublish',
        )
    return response
