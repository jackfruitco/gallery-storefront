import logging

from django.contrib import admin
from django.contrib import messages
from django.dispatch import receiver
from django.utils.safestring import mark_safe

from shopify_app.signals import sync_message
from .models import Color
from .models import Product
from .models import ProductCategory
from .models import ProductImage
from .models import ProductOption
from .models import ProductOptionValue
from .models import ProductVariant

logger = logging.getLogger(__name__)


class MediaUploadInline(admin.StackedInline):
    model = ProductImage
    extra = 1
    max_num = 9

    readonly_fields = [
        "resource_url",
    ]


class CreateVariantInLine(admin.StackedInline):
    model = ProductVariant
    extra = 0

    fieldsets = [
        (
            None,
            {
                "fields": [
                    "options",
                    "price",
                    "inv_policy",
                    # 'location',
                    "inv_name",
                    "oh_quantity",
                ]
            },
        ),
    ]


@admin.register(ProductOptionValue)
class ProductOptionValueAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "option",
                    "value",
                ]
            },
        ),
    ]


@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "product",
                    "name",
                    "position",
                ]
            },
        ),
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ("shopify_global_id", "created_at", "modified_at")

    def get_fieldsets(self, request, obj=None) -> tuple:
        default_fieldsets = [
            (
                None,
                {
                    "fields": (
                        "name",
                        ("description", "category"),
                    )
                },
            ),
            (
                None,
                {
                    "classes": ("collapse",),
                    "fields": (
                        "status",
                        "feature",
                    ),
                },
            ),
            (
                "Product Data",
                {
                    "classes": ("collapse",),
                    "fields": (
                        ("length", "length_unit"),
                        ("width", "width_unit"),
                        ("height", "height_unit"),
                        ("weight", "weight_unit"),
                    ),
                },
            ),
        ]

        advanced_fieldsets = [
            (
                "Shopify Storefront",
                {
                    "classes": ("collapse",),
                    "description": "Advanced Options to Sync with Shopify",
                    "fields": (
                        ("shopify_sync", "shopify_global_id"),
                        "shopify_status",
                        "base_price",
                    ),
                },
            ),
            (
                None,
                {"classes": ("collapse",), "fields": (("created_at", "modified_at"),)},
            ),
        ]

        # If object doesn't yet exist, only display default fieldsets
        # Otherwise, display all fieldsets
        if obj is None:
            return tuple(default_fieldsets)
        else:
            return tuple((default_fieldsets.__add__(advanced_fieldsets)))

    inlines = [
        MediaUploadInline,
        # CreateVariantInLine,
    ]

    list_display = ["name", "status", "feature", "shopify_sync", "shopify_status"]
    list_filter = ["category", "feature", "status", "shopify_sync"]
    search_fields = ["name", "description", "shopify_global_id"]

    def save_model(self, request, obj, form, change):
        @receiver(sync_message)
        def add_sync_message(
            sender,
            level=messages.INFO,
            message="Contact your Shopify Partner for assistance.",
            **kwargs
        ):
            """Signal handler to add message when sync error occurs"""
            messages.add_message(request, level, mark_safe(message))

        super(ProductAdmin, self).save_model(request, obj, form, change)


admin.site.register(ProductCategory)
admin.site.register(Color)
