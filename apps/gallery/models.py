import django_filters
from autoslug import AutoSlugField
from django.db import models
import logging, json
from apps.shopify_app.models import ShopifyAccessToken
from apps.shopify_app.api_connectors import _shop_sync, _shop_publish, _shop_product_delete, _shop_create_media

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

    # Product information
    category = models.ManyToManyField('ProductCategory')
    description = models.TextField(blank=True)

    # Site Gallery Display Data
    display = models.BooleanField(default=True, help_text=
    "If selected, this product will be displayed in Site Gallery")

    # Shopify Store Data
    shop_sync = models.BooleanField(
        default=False,
        help_text="If selected, this product's data will synced with Shopify and "
                  "available via the Shopify Online Store and Shopify POS. Please note, "
                  "updates made via Shopify Admin will be overridden, and do not sync with"
                  "this site.")
    shop_global_id  = models.CharField(max_length=100, blank=True, help_text="Shopify Global productID", editable=False)
    shop_status = models.CharField(max_length=10, default="DRAFT",
                                   choices={
                                       "ACTIVE": "Active",
                                       "DRAFT": "Draft",
                                       "ARCHIVED": "Archived"})
    sku = models.CharField(max_length=50, blank=True)
    price = models.FloatField(default=0, help_text="If item is not synced with Shopify, enter price as '0'.")
    primary_color = models.ForeignKey(Color, on_delete=models.CASCADE)

    def get_key_image(self):
        return ProductImage.objects.filter(fk_product=self, key_image=True).first()

    def get_images(self):
        return ProductImage.objects.filter(fk_product=self.pk).filter(key_image=False).all()[:4]

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if self.shop_sync:
            response = _shop_sync(self)
            if not self.shop_global_id:
                self.shop_global_id = json.loads(response)['data']['productSet']['product']['id']
                self.save()
            _shop_publish(self.shop_global_id)
        super().save(**kwargs)

    def delete(self, **kwargs):
        if self.shop_global_id:
            _shop_product_delete(self.shop_global_id)
        super().delete(**kwargs)


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

    def save(self, **kwargs):
        super().save(**kwargs)
        if self.fk_product.shop_global_id:
           _shop_create_media(self)

    class ProductFilter(django_filters.FilterSet):
        name = django_filters.CharFilter(lookup_expr='ic')
