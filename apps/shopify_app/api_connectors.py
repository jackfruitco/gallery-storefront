from apps.shopify_app.models import ShopifyAccessToken
from django.apps import apps
from django.utils.text import slugify
import json, shopify, logging
from .signals import shop_sync_error

logger = logging.getLogger(__name__)

shop_url = apps.get_app_config('shopify_app').SHOPIFY_URL
api_version = apps.get_app_config('shopify_app').SHOPIFY_API_VERSION


def error_parser(response, operation_name):
    """Parse JSON response for 'errors' or 'userError' and construct signals and logging"""
    if 'errors' in response:
        response = {
            "message": response['errors'][0]['message'],
            "field": response['errors'][0]['locations']
            }
        success = False
    elif response['data'][operation_name]['userErrors']:
        response = {
            "message": response['data'][operation_name]['userErrors'][0]['message'],
            "field": response['data'][operation_name]['userErrors'][0]['field']
            }
        success = False
    else: success = True

    # Logging and Signaling
    # Signal receiver is at ProductAdmin.save_model() to add_message
    msg = "%s GraphQL execution %s: %s" % (
        _product_set.__name__, 'succeeded' if success else 'failed',  response)
    if not success:
        logger.error(msg=msg)
        shop_sync_error.send(sender=_product_set.__name__, response=response['message'])
    else: logger.info(msg=msg)

    return success, response


def get_token_or_error() -> (bool, str):
    if ShopifyAccessToken.objects.filter(user=1).exists():
        return True, ShopifyAccessToken.objects.get(user=1).access_token
    else:
        return False, None

def shop_sync(obj, **kwargs) -> (bool, str):
    """Syncs product with Shopify Admin using various GraphQL mutations"""
    # returns: (success as bool, response as string)

    # Attempt to get Shopify Token.If token not found, exit function and return error
    token_exists, token = get_token_or_error()
    if not token_exists:
        # FUTURE FEAT: add link to error message
        msg = "token does not exist - are you authorized with Shopify?"
        logger.error("ShopifySync failed: %s" % msg)
        return False, msg

    # Open GraphQL document
    document = open('/app/apps/shopify_app/product_mutations.graphql', 'r').read()

    if kwargs['productDelete']:
        _product_delete(obj, token, document)
        return error_parser(obj, "productDelete")

    # execute productSet GraphQL mutation to sync Product with Shopify
    # if productSet fails, immediately exit sync function
    success, response = _product_set(obj, token, document)

    if not success:
        return False, response
    prod_gid = response['data']['productSet']['product']['id']
    # logger.info("GraphQL execution success: %s (productSet: %s)" %
    #             (success, prod_gid))

    # if mutation_success, publish product to sales channels
    # if publishablePublish fails, log quietly but continue sync
    # mutation error will be logged and message displayed to user
    for publication in apps.get_app_config('shopify_app').SHOPIFY_PUBLICATIONS:
        _publishable_publish(obj, token, document, prod_gid, publication)

    return True, response

def _product_set(obj, token, document) -> (bool, str):
    """Sync product with Shopify Admin using GraphQL mutation 'createProductSynchronous'"""
    operation_name = 'createProductSynchronous'

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
                operation_name=operation_name,
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
                operation_name=operation_name,
            )
    return error_parser(json.loads(response), operation_name)

# @shopify_token_required
def _publishable_publish(obj, token, document, prod_id, publication) -> (bool, str):
    """Publish product to Shopify publication using GraphQL mutation 'publishablePublish'"""
    # ! BUG: get access_token for user logged in
    operation_name='publishablePublish'

    with shopify.Session.temp(shop_url, api_version, token):
        response = shopify.GraphQL().execute(
            query=document,
            variables={
                "id": prod_id,
                "input": {
                    "publicationId": publication["id"],
                }
            },
            operation_name=operation_name,
        )

    return error_parser(json.loads(response), operation_name)


def _product_delete(obj, token, document):
    """Delete product from Shopify Admin using GraphQL mutation 'productDelete'"""
    operation_name = 'productDelete'

    with shopify.Session.temp(shop_url, api_version, token):
        response = shopify.GraphQL().execute(
            query=document,
            variables={
                "input": {
                    "id": obj.shop_global_id,
                }
            },
            operation_name=operation_name,
        )

    return error_parser(json.loads(response), operation_name)


def _shop_create_media(obj, token, document):
    """Sync product media in Shopify Admin using GraphQL mutation 'productCreateMedia'"""
    operation_name = 'productCreateMedia'

    #! BUG: remove hardcoded domain link
    img_url = 'http://%s%s' % ('localhost', obj.image.url)

    with shopify.Session.temp(shop_url, api_version, token):
        response = shopify.GraphQL().execute(
            query=document,
            variables={
                "media": {
                    "alt": obj.description,
                    "mediaContentType": "IMAGE",
                    "originalSource": img_url,
                },
                "productId": obj.fk_product.shop_global_id
            },
        operation_name=operation_name,
        )
    return error_parser(json.loads(response), operation_name)
