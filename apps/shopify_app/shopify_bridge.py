from apps.shopify_app.models import ShopifyAccessToken
from django.apps import apps
from django.utils.text import slugify
import json, shopify, logging
from django.contrib import messages
from .signals import sync_message

logger = logging.getLogger(__name__)

shop_url = apps.get_app_config('shopify_app').SHOPIFY_URL
api_version = apps.get_app_config('shopify_app').SHOPIFY_API_VERSION


def sync_setup() -> (str, str):
    """Syncs product with Shopify Admin using various GraphQL mutations"""

    # Attempt to get Shopify Token. If token not found, exit function and return error
    token_exists, token = get_token_or_error()
    if not token_exists:
        # FUTURE FEAT: add link to error message
        msg = "token does not exist - are you authorized with Shopify?"
        return {"errors": [{'message': msg, 'locations': sync_setup.__name__}]}

    # Open GraphQL document
    document = open('/app/apps/shopify_app/product_mutations.graphql', 'r').read()

    return {"token": token, "document": document}


def get_token_or_error() -> (bool, str):
    if ShopifyAccessToken.objects.filter(user=1).exists():
        return True, ShopifyAccessToken.objects.get(user=1).access_token
    else:
        return False, None


def product_set(obj) -> (bool, str):
    """Sync product with Shopify Admin using GraphQL mutation 'createProductSynchronous'"""
    operation_name = 'productSet'

    success, config = error_parser(sync_setup(), sync_setup.__name__, obj)
    if not success: return False, config

    with shopify.Session.temp(shop_url, api_version, config['token']):
        if obj.shopify_global_id:
            response = shopify.GraphQL().execute(
                query=config['document'],
                variables={
                    "synchronous": True,
                    "productSet": {
                        "title": obj.name,
                        "descriptionHtml": "<p>%s</p>" % obj.description,
                        "id": obj.shopify_global_id,
                        "handle": slugify(obj.name),
                        # "productType": self.category.name,
                        "status": obj.shopify_status,
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
                query=config['document'],
                variables={
                    "synchronous": True,
                    "productSet": {
                        "title": obj.name,
                        "descriptionHtml": "<p>%s</p>" % obj.description,
                        # "id": self.shopify_global_id,
                        "handle": slugify(obj.name),
                        # "productType": self.category.name,
                        "status": obj.shopify_status,
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
    return error_parser(json.loads(response), operation_name, obj)


def publish(obj, publication) -> (bool, str):
    """Publish product to Shopify publication using GraphQL mutation 'publishablePublish'"""
    # ! BUG: get access_token for user logged in
    operation_name='publishablePublish'

    success, config = error_parser(sync_setup(), sync_setup.__name__, obj)
    if not success: return False, config

    with shopify.Session.temp(shop_url, api_version, config['token']):
        response = shopify.GraphQL().execute(
            query=config['document'],
            variables={
                "id": obj.shopify_global_id,
                "input": {
                    "publicationId": publication["id"],
                }
            },
            operation_name=operation_name,
        )

    return error_parser(json.loads(response), operation_name, obj, publication=publication)


def product_delete(obj):
    """Delete product from Shopify Admin using GraphQL mutation 'productDelete'"""
    operation_name = 'productDelete'

    success, config = error_parser(sync_setup(), sync_setup.__name__, obj)
    if not success: return False, config

    with shopify.Session.temp(shop_url, api_version, config['token']):
        response = shopify.GraphQL().execute(
            query=config['document'],
            variables={
                "input": {
                    "id": obj.shopify_global_id,
                }
            },
            operation_name=operation_name,
        )

    return error_parser(json.loads(response), operation_name, obj)


def create_media(obj):
    """Sync product media in Shopify Admin using GraphQL mutation 'productCreateMedia'"""
    operation_name = 'productCreateMedia'

    success, config = error_parser(sync_setup(), sync_setup.__name__, obj)
    if not success: return False, config

    #! BUG: remove hardcoded domain link
    img_url = 'http://%s%s' % ('localhost', obj.image.url)

    with shopify.Session.temp(shop_url, api_version, config['token']):
        response = shopify.GraphQL().execute(
            query=config['document'],
            variables={
                "media": {
                    "alt": obj.description,
                    "mediaContentType": "IMAGE",
                    "originalSource": img_url,
                },
                "productId": obj.fk_product.shopify_global_id
            },
        operation_name=operation_name,
        )
    return error_parser(json.loads(response), operation_name, obj)


def error_parser(response, operation_name, obj, **kwargs):
    """Parse JSON response for 'errors' or 'userError' and construct signals and logging"""
    if 'errors' in response:
        response = {
            "message": response['errors'][0]['message'],
            "field": response['errors'][0]['locations']
            }
        success = False
    elif 'data' in response and response['data'][operation_name]['userErrors']:
        response = {
            "message": response['data'][operation_name]['userErrors'][0]['message'],
            "field": response['data'][operation_name]['userErrors'][0]['field']
            }
        success = False
    else: success = True

    # Logging and Signaling
    # Signal receiver is at ProductAdmin.save_model() to add_message
    # Success Signal only sent for productSet; publishablePublish will succeed quietly
    msg = "GraphQL execution %s: %s" % ('succeeded' if success else 'failed',  response)
    if not success:
        logger.error(msg=msg)
        if operation_name == sync_setup.__name__:
            sync_message.send(sender=operation_name, level=messages.ERROR,
                              message='The product "%s" could not be synced to Shopify (%s).' %
                                      (obj.name, response['message']))
        else:
            if 'publication' not in kwargs: publication='publication'
            else: publication = kwargs['publication']['name']
            sync_message.send(sender=operation_name, level=messages.WARNING,
                              message='The product "%s" failed to publish to Shopify %s (%s). Contact your Shopify Partner.' %
                               (obj.name, publication, response['message']))
    else:
        logger.info(msg=msg)
        if operation_name == 'productSet':
            sync_message.send(sender=operation_name, level=messages.SUCCESS,
                              message='The product "%s" synced successfully to Shopify in %s status!' %
                                      (obj.name, obj.shopify_status))

    return success, response