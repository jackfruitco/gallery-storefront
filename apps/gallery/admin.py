from django.contrib import admin, messages
from django.dispatch import receiver
from apps.shopify_app.signals import sync_message
from .models import Product, ProductImage, Color, ProductCategory
import logging

logger = logging.getLogger(__name__)

class MediaUploadInline(admin.StackedInline):
    model = ProductImage
    extra = 1
    max_num = 4

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ("shop_global_id", "created_at", "modified_at")

    fieldsets = [
        (None, {"fields": ["name", "category", "description", "primary_color"]}),
        ("Website Options", {"fields": ["display"]}),
        ("Storefront", {"fields": ["shop_sync", "shop_global_id","shop_status","price","sku"]}),
        ("Technical Data", {"fields": ["created_at", "modified_at"]})
    ]

    inlines = [MediaUploadInline]
    list_display = ["name", "display", "shop_sync", "shop_status"]
    list_filter = ["category", "display", "shop_sync"]
    search_fields = ["name", "description", "shop_global_id"]

    def save_model(self, request, obj, form, change):
        @receiver(sync_message)
        def add_sync_message(sender, level=messages.INFO, message='Contact your Shopify Partner for %s', **kwargs):
            """Signal handler to add message when shop sync error occurs"""
            message = message % obj.name
            messages.add_message(request, level, message)
        super(ProductAdmin, self).save_model(request, obj, form, change)

admin.site.register(ProductCategory)
admin.site.register(Color)