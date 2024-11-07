import django_filters
import shopify
from autoslug import AutoSlugField
from django.apps import apps
from django.db import models
import logging, json
from apps.shopify_app.decorators import shop_login_required, shopify_token_required
from apps.shopify_app.models import ShopifyAccessToken

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_image_path(instance, filename):
    return "images/products/{0}/{1}".format(instance.fk_product.pk, instance.slug + "." + filename.split('.')[-1])


class ProductCategory(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    # product information
    category = models.ManyToManyField('ProductCategory')
    description = models.TextField(blank=True)

    # display information
    display = models.BooleanField(default=True, help_text="Display this product in website gallery")

    # Shopify data
    available_for_sale = models.BooleanField(default=False)
    shopify_sync = models.BooleanField(default=False, help_text="Sync this item with Shopify")
    shop_GID  = models.CharField(max_length=100, blank=True, help_text="Shopify productID", editable=False)
    sku = models.CharField(max_length=50, blank=True)
    price = models.FloatField(null=True, blank=True)

    primary_color = models.ForeignKey(Color, on_delete=models.CASCADE)

    def get_key_image(self):
        return ProductImage.objects.filter(fk_product=self, key_image=True).first()
    def get_images(self):
        return ProductImage.objects.filter(fk_product=self.pk).filter(key_image=False).all()[:4]

    def __str__(self):
        return self.name

    @shopify_token_required
    def shopify_sync(self):
        """push item to shopify as new product"""
        shop_url = apps.get_app_config('shopify_app').SHOPIFY_URL
        api_version = apps.get_app_config('shopify_app').SHOPIFY_API_VERSION

        # below needs error handling for if token does not exist. Consider shop login decorator
        token = ShopifyAccessToken.objects.get(user=1).access_token
        document = open('/app/apps/gallery/product_mutations.graphql', 'r').read()

        with shopify.Session.temp(shop_url, api_version, token):
            response = shopify.GraphQL().execute(
                query=document,
                variables={
                    "synchronous": True,
                    "productSet": {
                        "title": self.name,
                        "descriptionHtml": "<i>%s</i>" % self.description,
                        "status": "ACTIVE",
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
                operation_name='createProductAsynchronous',
            )

        # BROKEN BUG
        # _var = json.loads(response)['data']['productSet']['product']['id']
        # obj = Product.objects.get(self)
        # obj.shop_GID = _var
        # obj.save()

        logger.warning(json.loads(response)['data']['productSet']['product']['id'])
        # logger.warning(Product.shop_GID)

        return response

    def save(self, **kwargs):
        _shop_sync = None
        if self.shopify_sync and not self.shop_GID:
            self.shop_GID = json.loads(self.shopify_sync())['data']['productSet']['product']['id']
            self.save()
        super().save(**kwargs)





class ProductImage(models.Model):
    fk_product = models.ForeignKey(Product, on_delete=models.CASCADE)
    key_image = models.BooleanField(default=False)
    priority = models.PositiveSmallIntegerField(default=10)
    description = models.CharField(max_length=100, blank=False,
                                   help_text="3-5 words describing the image")
    slug = AutoSlugField(populate_from='description', unique_with='fk_product', always_update=True)
    # credit = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    image = models.ImageField(upload_to=get_image_path)

    def __str__(self):
        return self.description

    class ProductFilter(django_filters.FilterSet):
        name = django_filters.CharFilter(lookup_expr='ic')
