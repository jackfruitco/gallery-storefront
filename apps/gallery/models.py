import logging

from autoslug import AutoSlugField
from django.apps import apps
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from GalleryStorefront.config import STOREFRONT_URL

from apps.shopify_app import shopify_bridge
from apps.shopify_app.models import ShopifyAccessToken

from apps.shopify_app import shopify_bridge
from apps.shopify_app.models import ShopifyAccessToken
from apps.store.context_processors import store_url, locations

logger = logging.getLogger(__name__)

def get_image_path(instance, filename):
    return "images/products/{0}/{1}".format(
        instance.fk_product.pk,
        instance.slug + "." + filename.split('.')[-1]
    )


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

    class Status(models.TextChoices):
        DRAFT = "DRAFT", _("Draft")
        ACTIVE = "ACTIVE", _("Active")
        ARCHIVED = "ARCHIVED", _("Archived")

    # Product information
    category = models.ManyToManyField('ProductCategory')
    description = models.TextField(blank=True)
    slug = AutoSlugField(
        populate_from='name',
        unique=True,
        always_update=True
    )

    choices = {
        "DRAFT": "Draft",
        "ACTIVE": "Active",
        "ARCHIVED": "Archived"
    }

    # Site Options
    status = models.CharField(
        max_length=10,
        verbose_name="Enable Site Gallery",
        choices=Status.choices,
        default=Status.ACTIVE,
        help_text="Enable to display this product in Site Gallery"
    )
    feature = models.BooleanField(
        default=True,
        verbose_name="Enable Featured Product",
        help_text="Enable to display this product on "
                  "the Homepage as a featured product."
    )

    @property
    def display(self)-> bool:
        """Used to check if Bool to display on gallery website."""
        return True if self.status == "ACTIVE" else False

    # Shopify Store Data
    shopify_sync = models.BooleanField(
        default=False,
        verbose_name="Enable ShopSync",
        help_text="Enable to automatically sync product with Shopify Admin. "
                  " Please note, updates made in Shopify Admin will be "
                  "overridden, and do not sync with the product "
                  "database. A Shopify Access Token is required!"
    )
    shopify_global_id  = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        editable=False,
        help_text="Shopify Global productID",
    )
    shopify_status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    base_price = models.FloatField(
        default=0,
        blank=True,
        null=True,
        help_text="Variant pricing will override this."
    )
    sku = models.CharField(
        max_length=50,
        blank=True
    )

    length = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)

    class MeasurementUnits(models.TextChoices):
        INCHES = "IN", _("Inches")
        CENTIMETERS = "CM", _("Centimeters")

    class WeightUnits(models.TextChoices):
        POUNDS = "LB", _("Pounds")
        OUNCES = "OZ", _("Ounces")
        GRAMS = "G", _("Grams")
        KILOGRAMS = "KG", _("Kilograms")

    length_unit = models.CharField(max_length=10, null=True, blank=True,
                                   choices=MeasurementUnits.choices,
                                   default=MeasurementUnits.INCHES)
    width_unit = models.CharField(max_length=10, null=True, blank=True,
                                  choices=MeasurementUnits.choices,
                                  default=MeasurementUnits.INCHES)
    height_unit = models.CharField(max_length=10, null=True, blank=True,
                                   choices=MeasurementUnits.choices,
                                   default=MeasurementUnits.INCHES)
    weight_unit = models.CharField(max_length=10, null=True, blank=True,
                                   choices=WeightUnits.choices,
                                   default=WeightUnits.OUNCES)

    # START deprecated field(s)
    primary_color = models.ForeignKey(Color, on_delete=models.CASCADE,
                                      blank=True, null=True)
    # END deprecated field(s)

    def get_feature_image(self):
        """Return a single image that is featured."""
        return ProductImage.objects.filter(
            fk_product=self, feature_image=True).first()

    def get_images(self) -> object:
        """Return all images EXCEPT the featured image."""
        return ProductImage.objects.filter(
            fk_product=self.pk).filter(feature_image=False).all()[:4]

    def get_variants(self) -> list:
        return ProductVariant.objects.filter(product=self)

    def format_variants(self) -> list:
        list_ = []
        for variant in self.get_variants():
            options_ = []
            for optionValue in variant.options.all():
                options_.append({
                    'optionName': optionValue.option.name,
                    'name': optionValue.value,

                })
            list_.append({
                'price': variant.price,
                'sku': (variant.sku, '') [
                    variant.sku is not None or
                    variant.sku == ''],
                'inventoryPolicy' : (variant.inv_policy, 'DENY') [
                    variant.inv_policy != 'CONTINUE'],
                'optionValues': options_
            })
        return list_

    def get_options(self) -> list:
        """Return all ProductOptions associated with this product."""
        # return ProductOption.objects.filter(product=self).all()
        return ProductOption.objects.filter(product=self)

    def format_options(self) -> list:
        list_ = []
        # v = []
        for option in self.get_options():
            # for value in option.values:
            #     v.append({'name': option.value})
            list_.append({
                'name': option.name,
                'position': option.position,
                'values': option.format_values()
            })
        return list_

    def get_shop_url(self) -> str:
        """Return Shopify Product Page URL."""
        url = STOREFRONT_URL
        if url.endswith("/"): url = url[:-1]
        return '%s/products/%s' % (url, self.slug)

    def get_absolute_url(self) -> bytes:
        """Return URL to this product."""
        return reverse(
            viewname='gallery:product-detail',
            kwargs={'category': self.category.name, 'slug': self.slug}
        )

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if self.shopify_sync:
            success, data = shopify_bridge.product_set(self)
            if success:
                product_id = data['data']['productSet']['product']['id']
                self.shopify_global_id = product_id
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
    """Store image for specified product."""
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    fk_product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE
    )
    feature_image = models.BooleanField(
        default=False,
        help_text="Enable to display image as the featured "
                  "image. The featured image is used as the product's "
                  "primary image"
    )
    description = models.CharField(
        max_length=100,
        blank=False,
        help_text="3-5 words describing the image"
    )
    slug = AutoSlugField(
        populate_from='description',
        unique_with='fk_product',
        always_update=True
    )
    image = models.ImageField(
        upload_to=get_image_path
    )
    resource_url = models.URLField(
        max_length=500, blank=True,
        help_text="Shopify resourceURL if uploaded to Shopify"
    )

    @property
    def get_absolute_url(self) -> str:
        """Returns absolute url of image"""
        if settings.STORAGES['default']['BACKEND'].endswith('S3Storage'):
            url = ''
        else:
            url = 'http://localhost/'
        url += self.image.url
        return url

    def __str__(self):
        return self.description

    def save(self, **kwargs):

        super().save(**kwargs)
        if self.fk_product.shopify_global_id:
           shopify_bridge.create_media(self)
        if self.fk_product.shopify_sync and self.fk_product.shopify_global_id:
            success, response = shopify_bridge.staged_uploads_create(self)


class ProductOptionValue(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    value = models.CharField(max_length=100, verbose_name="Option Value")
    option = models.ForeignKey("ProductOption", on_delete=models.CASCADE,
                             verbose_name="Option Name")

    def __str__(self):
        return '%s %s' % (self.option.name, self.value)

    def save(self, **kwargs):
        logger.debug('...saving model: %s' % self.__class__.__name__)
        super().save(**kwargs)


class ProductOption(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    position = models.IntegerField()
    name = models.CharField(
        max_length=100, verbose_name="Option Name",
        help_text='e.g. "Color" or "Pattern"')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=True, null=True)
    values = models.ManyToManyField(
        "ProductOptionValue", blank=True, verbose_name="Option Values",
        help_text='Values for this Option (e.g. "Red", "Blue", etc.')

    def get_values(self) -> list:
        """Return QuerySet with values associated with this Option."""
        return ProductOptionValue.objects.filter(option=self)

    def format_values(self) -> list:
        list_ = []
        for value in self.get_values():
            list_.append({'name': value.value})
        return list_

    def __str__(self):
        return '%s' % self.name

    def save(self, **kwargs):
        logger.debug('...saving model: %s' % self.__class__.__name__)
        super().save(**kwargs)


class ProductVariant(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    options = models.ManyToManyField(
        "ProductOptionValue", blank=True, verbose_name="Options",)

    shopify_id = models.CharField(max_length=100, blank=True)
    inv_policy = models.CharField(
        max_length=100, default='DENY', verbose_name="Inventory Policy",
        choices={'DENY': "Deny",'CONTINUE': "Continue"},
        help_text='When a product has no inventory available, this policy '
                  'determines if new orders should continue to process, '
                  'or be denied.')
    sku = models.CharField(max_length=100, blank=True)
    location = models.CharField(
        max_length=100, choices=locations, verbose_name="Inventory Location")
    oh_quantity = models.IntegerField(
        default=1, verbose_name="On Hand Quantity")
    price = models.FloatField(default=0, verbose_name="Variant Price")

    # START deprecated field(s):
    inv_name = models.CharField(
        max_length=100, default="available", verbose_name="Inventory Name",
        choices={"available": "Available","on hand": "On Hand"})
    # END deprecated field(s)

    def format_options(self) -> list:
        """Returns list of options in Dict ready for GraphQL API"""
        list_ = []
        for option in self.options.all():
            list_.append({
                'name': option.option.name,
                'value': option.value,
            })
        return list_

    def __str__(self):
        s = ''
        for option in self.options.all():
            s = s + '%s, ' % option.value
        return '%s (%s)' % (self.product.name, None if s == '' else s[:-2])

    def save(self, **kwargs):
        if self.product.shopify_sync and self.product.shopify_global_id:
            pass
        logger.debug('...saving model: %s' % self.__class__.__name__)
        super().save(**kwargs)



