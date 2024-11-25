import django_filters
from autoslug import AutoSlugField
from django.db import models
from apps.shopify_app.models import ShopifyAccessToken
from apps.shopify_app import shopify_bridge
from django.apps import apps

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
    display = models.BooleanField(default=True, verbose_name="Gallery Display Enabled", help_text=
    "If selected, this product will be displayed in Site Gallery")

    # Shopify Store Data
    shopify_sync = models.BooleanField(
        default=False,
        verbose_name="Shopify Sync Enabled",
        help_text="If selected, this product's data will synced with Shopify and "
                  "available via the Shopify Online Store and Shopify POS. Please note, "
                  "updates made via Shopify Admin will be overridden, and do not sync with "
                  "this site.")
    shopify_global_id  = models.CharField(max_length=100, blank=True, help_text="Shopify Global productID", editable=False)
    shopify_status = models.CharField(max_length=10, default="DRAFT",
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
        if self.shopify_sync:
            success, response = shopify_bridge.product_set(self)
            if success: self.shopify_global_id = response['data']['productSet']['product']['id']
        if (update_fields := kwargs.get("update_fields")) is not None:
            kwargs["update_fields"] = {"shopify_global_id"}.union(update_fields)
        super().save(**kwargs)
        if self.shopify_sync and self.shopify_global_id:
            for publication in apps.get_app_config('shopify_app').SHOPIFY_PUBLICATIONS:
                shopify_bridge.publish(self, publication)

    def delete(self, **kwargs):
        if self.shopify_global_id:
            shopify_bridge.product_delete(self)
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
        # if self.fk_product.shopify_global_id:
        #    shopify_bridge.create_media(self)

    class ProductFilter(django_filters.FilterSet):
        name = django_filters.CharFilter(lookup_expr='ic')
