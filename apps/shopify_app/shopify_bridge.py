import json
import logging
from os.path import splitext
from urllib.parse import urlparse

import requests
import shopify
from django.apps import apps
from django.conf import settings
from django.contrib import messages

from apps.shopify_app.models import ShopifyAccessToken
from .signals import sync_message

logger = logging.getLogger(__name__)

shop_url = apps.get_app_config('shopify_app').SHOPIFY_URL
api_version = apps.get_app_config('shopify_app').SHOPIFY_API_VERSION

def get_ext(url):
    """Return the filename extension from url, or ''."""
    parsed = urlparse(url)
    root, ext = splitext(parsed.path)
    return ext  # or ext[1:] if you don't want the leading '.'


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

    variables = {
        "synchronous": True,
        "productSet": {
            "title": obj.name,
            "descriptionHtml": "<p>%s</p>" % obj.description,
            "handle": obj.slug,
            "status": obj.shopify_status,
        }
    }

    # Add Shopify GID if available, otherwise, omit to create new item.
    if obj.shopify_global_id is not None:
        variables['productSet']['id'] = obj.shopify_global_id

    # Add variant and option values if exists,
    # otherwise, change to DefaultVariantOnly operation and omit.
    if obj.get_variants() is None:
        operation_name += 'DefaultVariantOnly'
        variables['price']
        logger.debug('No variants found for %s. Switching to DefaultVariantOnly mutation.' % obj.name)
    else:
        variables['productSet']['productOptions'] = obj.format_options()
        variables['productSet']['variants'] = obj.format_variants()

    logger.debug(variables)

    with shopify.Session.temp(shop_url, api_version, config['token']):
        response = shopify.GraphQL().execute(
            query=config['document'],
            variables=variables,
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


def create_media(obj, resource_url):
    """Sync product media in Shopify Admin using GraphQL mutation 'productCreateMedia'"""
    operation_name = 'productCreateMedia'

    success, config = error_parser(sync_setup(), sync_setup.__name__, obj)
    if not success: return False, config

    with shopify.Session.temp(shop_url, api_version, config['token']):
        response = shopify.GraphQL().execute(
            query=config['document'],
            variables={
                "media": {
                    "alt": obj.description,
                    "mediaContentType": "IMAGE",
                    "originalSource": resource_url,
                },
                "productId": obj.fk_product.shopify_global_id
            },
        operation_name=operation_name,
        )
    return error_parser(json.loads(response), operation_name, obj)


def staged_uploads_create(obj):
    """Creates staged upload targets to upload media to Shopify. Reference GraphQL API 'stagedUploadsCreate'"""
    operation_name = 'stagedUploadsCreate'

    success, config = error_parser(sync_setup(), sync_setup.__name__, obj)
    if not success: return False, config

    http_method = 'PUT'
    ext = get_ext(obj.image.url)

    with shopify.Session.temp(shop_url, api_version, config['token']):
        response = shopify.GraphQL().execute(
            query=config['document'],
            variables={
                "input": [
                    {
                        "filename": "%s%s" % (obj.description, ext),
                        "mimeType": "image/%s" % ext[1:],
                        "httpMethod": http_method,
                        "resource": "IMAGE"
                    },
                ]
            },
        operation_name=operation_name,
        )

    success, response = error_parser(json.loads(response), operation_name, obj)
    if not success: return success, response

    url = response['data']['stagedUploadsCreate']['stagedTargets'][0]['url']
    resource_url = response['data']['stagedUploadsCreate']['stagedTargets'][0]['resourceUrl']
    img_path = '%s%s' % (settings.BASE_DIR, obj.image.url)

    # logger.debug(img_path)
    # logger.debug(open(img_path, 'rb').read())

    http = {}
    params = {}

    if http_method == 'PUT':
        param_method = 'headers'
        # with open(img_path, "r") as f:
        http['files'] = {'file': open(img_path, 'rb').read()}
    elif http_method == 'POST':
        param_method = 'files'
        http[param_method]= {'file': open(img_path, "rb").read()}
    else: param_method = ['missing']

    for param in response['data']['stagedUploadsCreate']['stagedTargets'][0]['parameters']:
        params[param['name']] = param['value']
    http[param_method] = params

    for var in ['headers', 'files', 'data']:
        if var not in http: http[var] = None

    # HTTP PUT/POST request to upload media file to Shopify using url provided by GraphQL response
    requests.request(http_method, url, data=http['data'], headers=http['headers'], files=http['files'])

    success, response = create_media(obj, resource_url)

    # return error_parser(json.loads(response), operation_name, obj)
    return error_parser(response, 'productCreateMedia', obj)

def get_file_status(obj):
    """Queries product for all media. Reference GraphQL API '...'"""
    operation_name = 'getFileStatus'

    success, config = error_parser(sync_setup(), sync_setup.__name__, obj)
    if not success: return False, config

    with shopify.Session.temp(shop_url, api_version, config['token']):
        response = shopify.GraphQL().execute(
            query=config['document'],
            variables={
                "id": obj.shopify_global_id,
            },
        operation_name=operation_name,
        )

    # success, response = error_parser(json.loads(response), operation_name, obj)
    # if not success: return success, response
    logger.debug(response)
    return



def error_parser(response, operation_name, obj, **kwargs):
    """Parse JSON response for 'errors' or 'userError' and construct signals and logging"""
    success = True
    if 'errors' in response:
        success = False
        response = {
            "message": response['errors'][0]['message'],
            "field": response['errors'][0]['locations']
            }
    elif 'data' in response:
        user_error = []
        if 'userErrors' in response['data'][operation_name]: user_error = response['data'][operation_name]['userErrors']
        elif 'mediaUserErrors' in response['data'][operation_name]: user_error = response['data'][operation_name]['mediaUserErrors']

        if user_error:
            success = False
            response = {
                "message": user_error[0]['message'],
                "field": user_error[0]['field'][0]
                }

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
        elif operation_name == 'publishablePublish':
            if 'publication' not in kwargs: publication='publication'
            else: publication = kwargs['publication']['name']
            sync_message.send(sender=operation_name, level=messages.WARNING,
                              message='The product "%s" could not be published to Shopify %s (%s). Contact your Shopify Partner.' %
                                      (obj.name, publication, response['message']))
        elif operation_name == 'stagedUploadsCreate':
            sync_message.send(sender=operation_name, level=messages.WARNING,
                              message='The media "%s" could not be staged for upload to Shopify (%s). Contact your Shopify Partner' %
                                      (obj.description, response['message']))
        else:
            sync_message.send(sender=operation_name, level=messages.WARNING,
                              message="An unknown error occurred. Please contact your Shopify Partner")
    elif operation_name != sync_setup.__name__:
        logger.info(msg=msg)
        if operation_name == 'productSet':
            sync_message.send(sender=operation_name, level=messages.SUCCESS,
                              message='The product "%s" synced successfully to Shopify in %s status!' %
                                      (obj.name, obj.shopify_status.title()))

    return success, response

