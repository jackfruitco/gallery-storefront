import logging

import boto3
from autoslug import AutoSlugField
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from pilkit.processors import Thumbnail

from core.config import S3
from shopify_app import shopify_bridge
from shopify_app.apps import ShopifyAppConfig

logger = logging.getLogger(__name__)


def get_image_path(instance, filename):
    return "images/products/{0}/{1}".format(
        instance.fk_product.pk, instance.slug + "." + filename.split(".")[-1]
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
    category = models.ManyToManyField("ProductCategory")
    description = models.TextField(blank=True)
    slug = AutoSlugField(populate_from="name", unique=True, always_update=True)

    # Site Options
    status = models.CharField(
        max_length=10,
        verbose_name="Enable Site Gallery",
        choices=Status,
        default=Status.ACTIVE,
        help_text="Enable to display this product in Site Gallery",
    )
    feature = models.BooleanField(
        default=True,
        verbose_name="Enable Featured Product",
        help_text="Enable to display this product on "
        "the Homepage as a featured product.",
    )

    @property
    def is_active(self) -> bool:
        """Used to check if Bool to display on gallery website."""
        return True if self.status == "ACTIVE" else False

    # Shopify Store Data
    shopify_sync = models.BooleanField(
        default=False,
        verbose_name="Enable ShopSync",
        help_text="Enable to automatically sync product with Shopify Admin. "
        " Please note, updates made in Shopify Admin will be "
        "overridden, and do not sync with the product "
        "database. A Shopify Access Token is required!",
    )
    shopify_global_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        editable=False,
        help_text="Shopify Global productID",
    )
    shopify_status = models.CharField(
        max_length=10,
        choices=Status,
        default=Status.DRAFT,
    )
    base_price = models.FloatField(
        default=0,
        blank=True,
        null=True,
        help_text="Variant pricing will override this.",
    )
    sku = models.CharField(max_length=50, blank=True)

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

    length_unit = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        choices=MeasurementUnits,
        default=MeasurementUnits.INCHES,
    )
    width_unit = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        choices=MeasurementUnits,
        default=MeasurementUnits.INCHES,
    )
    height_unit = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        choices=MeasurementUnits,
        default=MeasurementUnits.INCHES,
    )
    weight_unit = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        choices=WeightUnits,
        default=WeightUnits.OUNCES,
    )

    def get_feature_image(self):
        """
        Return the featured ProductImage object for a product.

        :param self: Product Object
        :return: QuerySet
        """

        return ProductImage.objects.filter(fk_product=self, feature_image=True).first()

    def get_images(self) -> object:
        """
        Return QuerySet of images for a product, excluding featured image.

        :param self: Product Object
        :return: QuerySet
        """

        return (
            ProductImage.objects.filter(fk_product=self.pk)
            .filter(feature_image=False)
            .all()[:4]
        )

    def get_variants(self) -> list or None:
        """
        Return QuerySet of variants for a product.

        If no variants are found, return None.

        :param self: Product Object
        :return: QuerySet list, or None
        """

        if len(list_ := ProductVariant.objects.filter(product=self)) == 0:
            return None
        else:
            return list_

    def format_default_variant(self) -> tuple:
        """
        Return JSON-serializable dictionary for default variant only.

        :param self: Product Object
        :return: tuple (variants, options)
        """

        variants = [
            {
                "optionValues": [
                    {
                        "optionName": "Title",
                        "name": "Default Title",
                    }
                ],
                "price": self.base_price,
            }
        ]

        options = [{"name": "Title", "values": [{"name": "Default Title"}]}]

        return variants, options

    def format_variants(self) -> list:
        """
        Return JSON-serializable dictionary of variants for a product.

        Check if product has any variants. If no variants are found,
        return a list for the default variant using the product's base
        price. Otherwise, loop through each product variant and format
        the options in to match GraphQL implementation.

        :param self: Product Object
        :return: JSON-serializable dictionary
        """

        # If no variants found, raise error.
        # :BUG: add error handling.
        if len(self.get_variants()) == 0:
            pass

        # For each variant, append dict of values to list
        list_ = []
        for variant in self.get_variants():
            options_ = []

            # for each option, append dict of values to list
            for optionValue in variant.options.all():
                options_.append(
                    {
                        "optionName": optionValue.option.name,
                        "name": optionValue.value,
                    }
                )
            list_.append(
                {
                    "price": variant.price,
                    "sku": (variant.sku, "")[
                        variant.sku is not None or variant.sku == ""
                    ],
                    "inventoryPolicy": (variant.inv_policy, "DENY")[
                        variant.inv_policy != "CONTINUE"
                    ],
                    "optionValues": options_,
                }
            )
        return list_

    def get_options(self):
        """
        Return QuerySet of options for a product.

        :param self: Product Object
        :return: QuerySet
        """

        return ProductOption.objects.filter(product=self)

    def format_options(self) -> list:
        """
        Return JSON-serializable dictionary of options for a product.

        :param self: Product Object
        :return: JSON-serializable dictionary
        """

        list_ = []
        # v = []
        for option in self.get_options():
            # for value in option.values:
            #     v.append({'name': option.value})
            list_.append(
                {
                    "name": option.name,
                    "position": option.position,
                    "values": option.format_values(),
                }
            )
        return list_

    def get_shop_url(self, admin=False) -> str:
        """Return Shopify Product Page URL."""
        if not admin:
            url = ShopifyAppConfig.SHOP_DOMAIN

            # Strips trailing / if found, then adds slug
            if url.endswith("/"):
                url = url[:-1]
            url += "/products/%s" % self.slug
        else:
            # Split ID number off GID string, then add to admin url
            gid = self.shopify_global_id.split("/")[-1]
            url = "%s/products/%s" % (ShopifyAppConfig.ADMIN_URL, gid)
        return url

    def get_absolute_url(self) -> str:
        """Return URL to product."""
        return reverse(
            viewname="gallery:product-detail",
            kwargs={"category": self.category.first().name, "slug": self.slug},
        )

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if self.shopify_sync:
            success, data = shopify_bridge.product_set(self)
            if success:
                product_id = data["data"]["productSet"]["product"]["id"]
                self.shopify_global_id = product_id
        if (update_fields := kwargs.get("update_fields")) is not None:
            kwargs["update_fields"] = {"shopify_global_id"}.union(update_fields)
        super().save(**kwargs)
        if self.shopify_sync and self.shopify_global_id:
            for publication in ShopifyAppConfig.SHOPIFY_PUBLICATIONS:
                shopify_bridge.publish(self, publication)

    def delete(self, **kwargs):
        if self.shopify_global_id:
            shopify_bridge.product_delete(self)
        super().delete(**kwargs)


class ProductImage(models.Model):
    """Store image for specified product."""

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    description = models.CharField(
        max_length=100,
        blank=False,
        help_text="3-5 words describing the image",
    )

    slug = AutoSlugField(
        populate_from="description",
        unique_with="fk_product",
        always_update=True,
    )

    original = models.ImageField(
        upload_to=get_image_path,
        verbose_name="image",
        height_field="original_height",
        width_field="original_width",
    )

    original_height = models.PositiveIntegerField(
        editable=False,
        blank=True,
        null=True,
    )

    original_width = models.PositiveIntegerField(
        editable=False,
        blank=True,
        null=True,
    )

    thumbnail = ImageSpecField(
        source="original",
        processors=[Thumbnail(width=300, height=300, crop=False)],
        format="WEBP",
        options={"quality": 80},
    )

    logo = ImageSpecField(
        source="original",
        processors=[Thumbnail(width=600, height=600, crop=False)],
        format="WEBP",
        options={"quality": 80},
    )

    fk_product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
    )

    feature_image = models.BooleanField(
        default=False,
        help_text="Enable to display image as the featured "
        "image. The featured image is used as the product's "
        "primary image",
    )

    resource_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="Shopify resourceURL if uploaded to Shopify",
    )

    def get_file_data(self) -> bytes:
        """
        Retrieves S3 Object data from Cloudflare R2.

        This is primarily used to get object data in bytes for use in
        a PUT request to upload media to Shopify.

        :return: Bytes of Image Object
        """

        from botocore.client import Config

        # Initiate S3 Client
        conf = S3.get_config()
        s3_client = boto3.client(
            "s3",
            endpoint_url=conf["endpoint_url"],
            aws_access_key_id=conf["access_key"],
            aws_secret_access_key=conf["secret_key"],
            config=Config(signature_version=conf["signature_version"]),
        )

        # Retrieve S3 Object Key from image url
        # Strips endpoint url, then strips querystring
        base_url = "%s/%s/" % (conf["endpoint_url"], conf["bucket_name"])
        key = self.original.url[len(base_url) :].split("?")[0]

        # retrieves data of
        file_data = s3_client.get_object(
            Bucket=conf["bucket_name"],
            Key=key,
        )["Body"].read()

        return file_data

    @property
    def get_absolute_url(self) -> str:
        """Returns absolute url of image"""
        if settings.STORAGES["default"]["BACKEND"].endswith("S3Storage"):
            url = ""
        else:
            url = "http://localhost/"
        url += self.original.url
        return url

    def __str__(self):
        return self.description

    def save(self, **kwargs):

        super().save(**kwargs)
        if self.fk_product.shopify_sync and self.fk_product.shopify_global_id:
            shopify_bridge.staged_uploads_create(self)


class ProductOptionValue(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    value = models.CharField(max_length=100, verbose_name="Option Value")
    option = models.ForeignKey(
        "ProductOption", on_delete=models.CASCADE, verbose_name="Option Name"
    )

    def __str__(self):
        return "%s %s" % (self.option.name, self.value)

    def save(self, **kwargs):
        logger.debug("...saving model: %s" % self.__class__.__name__)
        super().save(**kwargs)


class ProductOption(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    position = models.IntegerField()
    name = models.CharField(
        max_length=100,
        verbose_name="Option Name",
        help_text='e.g. "Color" or "Pattern"',
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=True, null=True
    )
    values = models.ManyToManyField(
        "ProductOptionValue",
        blank=True,
        verbose_name="Option Values",
        help_text='Values for this Option (e.g. "Red", "Blue", etc.',
    )

    def get_values(self):
        """Return QuerySet with values associated with this Option."""
        return ProductOptionValue.objects.filter(option=self)

    def format_values(self) -> list:
        list_ = []
        for value in self.get_values():
            list_.append({"name": value.value})
        return list_

    def __str__(self):
        return "%s" % self.name

    def save(self, **kwargs):
        logger.debug("...saving model: %s" % self.__class__.__name__)
        super().save(**kwargs)


class ProductVariant(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    options = models.ManyToManyField(
        "ProductOptionValue",
        blank=True,
        verbose_name="Options",
    )

    shopify_id = models.CharField(max_length=100, blank=True)
    inv_policy = models.CharField(
        max_length=100,
        default="DENY",
        verbose_name="Inventory Policy",
        choices={"DENY": "Deny", "CONTINUE": "Continue"},
        help_text="When a product has no inventory available, this policy "
        "determines if new orders should continue to process, "
        "or be denied.",
    )
    sku = models.CharField(max_length=100, blank=True)
    location = models.CharField(
        max_length=100,
        #     choices=locations,
        verbose_name="Inventory Location",
    )
    oh_quantity = models.IntegerField(default=1, verbose_name="On Hand Quantity")
    price = models.FloatField(default=0, verbose_name="Variant Price")

    # START deprecated field(s):
    inv_name = models.CharField(
        max_length=100,
        default="available",
        verbose_name="Inventory Name",
        choices={"available": "Available", "on hand": "On Hand"},
    )
    # END deprecated field(s)

    def format_options(self) -> list:
        """Returns list of options in Dict ready for GraphQL API"""
        list_ = []
        for option in self.options.all():
            list_.append(
                {
                    "name": option.option.name,
                    "value": option.value,
                }
            )
        return list_

    def __str__(self):
        s = ""
        for option in self.options.all():
            s = s + "%s, " % option.value
        return "%s (%s)" % (self.product.name, None if s == "" else s[:-2])

    def save(self, **kwargs):
        if self.product.shopify_sync and self.product.shopify_global_id:
            pass
        logger.debug("...saving model: %s" % self.__class__.__name__)
        super().save(**kwargs)
