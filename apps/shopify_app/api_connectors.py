from pyexpat.errors import messages

from django.contrib.messages import success

from apps.shopify_app.decorators import shopify_token_required
from apps.shopify_app.models import ShopifyAccessToken
from django.apps import apps
from django.utils.text import slugify
import json, shopify, logging

logger = logging.getLogger(__name__)


shop_url = apps.get_app_config('shopify_app').SHOPIFY_URL
api_version = apps.get_app_config('shopify_app').SHOPIFY_API_VERSION
# token = ShopifyAccessToken.objects.get(user=1).access_token
# document = open('/app/apps/shopify_app/product_mutations.graphql', 'r').read()

def get_token_or_error() -> (bool, str):
    if ShopifyAccessToken.objects.filter(user=1).exists():
        return True, ShopifyAccessToken.objects.get(user=1).access_token
    else:
        return False, None

def shop_sync(self) -> (bool, str):
    """Syncs product with Shopify"""
    # returns: (success as bool, error_msg as string)
    # if bool = True, then no error
    # if bool = False, then error with error msg included

    # Attempt to get Shopify Token.If token not found, exit function and return error
    token_exists, token = get_token_or_error()
    if not token_exists:

        msg = 'token does not exist - are you authorized with Shopify?'
        logger.error("ShopifySync failed: %s" % msg)
        return False, msg

    # Open GraphQL document
    document = open('/app/apps/shopify_app/product_mutations.graphql', 'r').read()

    # execute productSet GraphQL mutation to sync Product with Shopify
    # if productSet fails, immediately exit sync function
    success, product_response = _product_set(self, token, document)

    if not success:
        return False, product_response
    prod_gid = product_response['data']['productSet']['product']['id']
    logger.info("GraphQL execution success: %s (productSet: %s)" %
                (success, prod_gid))

    # if mutation_success, publish product to sales channels
    # if publishablePublish fails, log quietly but continue sync
    # mutation error will be logged and message displayed to user
    shop_publications = apps.get_app_config('shopify_app').SHOPIFY_PUBLICATIONS
    status = {}
    for pub in shop_publications:
        success, response = _publishable_publish(self, token, document, prod_gid, pub["gid"])
        status[pub["gid"]] = {"success": success, "response": response}
        msg = "GraphQL execution (publishablePublish %s): %s" % (pub["gid"], status[pub["gid"]])
        if success: logger.info(msg)
        else: logger.error(msg)

    return True, product_response

def _product_set(obj, token, document) -> (bool, str):
    """Sync product with Shopify"""
    # document = open('/app/apps/shopify_app/product_mutations.graphql', 'r').read()

    with shopify.Session.temp(shop_url, api_version, token):
        if obj.shop_global_id:
            response = shopify.GraphQL().execute(
                query=document,
                variables={
                    "synchronous": True,
                    "productSet": {
                        "title": obj.name,
                        "descriptionHtml": "<p>%s</p>" % obj.description,
                        "id": obj.shop_global_id,
                        "handle": slugify(obj.name),
                        # "productType": self.category.name,
                        "status": obj.shop_status,
                        "productOptions": [
                            {
                                "name": "Color",
                                "position": 1,
                                "values": [
                                    {"name": obj.primary_color.name},
                                ]
                            }
                        ],
                        "variants": [
                            {
                                "optionValues": [{
                                    "optionName": "Color",
                                    "name": obj.primary_color.name,
                                }],
                                "price": obj.price,
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
                        "title": obj.name,
                        "descriptionHtml": "<p>%s</p>" % obj.description,
                        # "id": self.shop_global_id,
                        "handle": slugify(obj.name),
                        # "productType": self.category.name,
                        "status": obj.shop_status,
                        "productOptions": [
                            {
                                "name": "Color",
                                "position": 1,
                                "values": [
                                    {"name": obj.primary_color.name},
                                ]
                            }
                        ],
                        "variants": [
                            {
                                "optionValues": [{
                                    "optionName": "Color",
                                    "name": obj.primary_color.name,
                                }],
                                "price": obj.price,
                            },
                        ],
                    }
                },
                operation_name='createProductSynchronous',
            )

    response = json.loads(response)

    if not (response['data']['productSet']['userErrors']):
        success = True
    else: success = False

    return success, response

# @shopify_token_required
def _publishable_publish(obj, token, document, prod_gid, pub_id) -> (bool, str):
    # ! BUG: get access_token for user logged in
    with shopify.Session.temp(shop_url, api_version, token):
        response = shopify.GraphQL().execute(
            query=document,
            variables={
                "id": prod_gid,
                "input": {
                    "publicationId": pub_id,
                }
            },
            operation_name='publishablePublish',
        )
    response = json.loads(response)

    if not (response['errors']):
        success = True
    else: success = False

    return success, response

@shopify_token_required
def _shop_product_delete(product_global_id):
    # shop_url = apps.get_app_config('shopify_app').SHOPIFY_URL
    # api_version = apps.get_app_config('shopify_app').SHOPIFY_API_VERSION

    # ! BUG: add error handling for when token does not exist. Consider shop login decorator
    # ! BUG: get access_token for user logged in
    token = ShopifyAccessToken.objects.get(user=1).access_token
    document = open('/app/apps/shopify_app/product_mutations.graphql', 'r').read()

    with shopify.Session.temp(shop_url, api_version, token):
        response = shopify.GraphQL().execute(
            query=document,
            variables={
                "input": {
                    "id": product_global_id,
                }
            },
            operation_name='productDelete',
        )
    logger.info(json.loads(response))
    return response

@shopify_token_required
def _shop_create_media(self):
    # shop_url = apps.get_app_config('shopify_app').SHOPIFY_URL
    # api_version = apps.get_app_config('shopify_app').SHOPIFY_API_VERSION

    # ! BUG: add error handling for when token does not exist. Consider shop login decorator
    # ! BUG: get access_token for user logged in
    token = ShopifyAccessToken.objects.get(user=1).access_token
    document = open('/app/apps/shopify_app/product_mutations.graphql', 'r').read()

    #! BUG: remove hardcoded domain link
    img_url = 'http://%s%s' % ('localhost', self.image.url)

    with shopify.Session.temp(shop_url, api_version, token):
        response = shopify.GraphQL().execute(
            query=document,
            variables={
                "media": {
                    "alt": self.description,
                    "mediaContentType": "IMAGE",
                    "originalSource": img_url,
                },
                "productId": self.fk_product.shop_global_id
            },
        operation_name='productCreateMedia',
        )
    logger.info(json.loads(response))
    return response
