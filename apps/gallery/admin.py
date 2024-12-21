import logging

from django.contrib import admin, messages
from django.dispatch import receiver

from apps.shopify_app.signals import sync_message
from .models import Product, ProductImage, Color, ProductCategory, ProductVariant, ProductOption, ProductOptionValue

logger = logging.getLogger(__name__)

class MediaUploadInline(admin.StackedInline):
    model = ProductImage
    extra = 1
    max_num = 5

class CreateVariantInLine(admin.StackedInline):
    model = ProductVariant
    extra = 0

    fieldsets = [
        (None, {'fields': ['options', 'price', 'inv_policy', 'location', 'inv_name', 'oh_quantity'],}),
    ]

@admin.register(ProductOptionValue)
class ProductOptionValueAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['option','value',],}),
    ]

@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['product', 'name', 'position']}),
    ]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('shopify_global_id', 'created_at', 'modified_at')

    fieldsets = [
        (None, {'fields': ['name', 'category', 'description']}),
        ('Product Data', {'fields': ['length', 'length_unit', 'width', 'width_unit', 'height', 'height_unit', 'weight', 'weight_unit']}),
        ('Website Options', {'fields': ['status', 'feature']}),
        ('Storefront', {'fields': ['shopify_sync', 'shopify_global_id','shopify_status','sku']}),
        ('Technical Data', {'fields': ['created_at', 'modified_at']})
    ]
    inlines = [
        MediaUploadInline,
        CreateVariantInLine,
    ]

    list_display = ['name', 'status', 'feature', 'shopify_sync', 'shopify_status']
    list_filter = ['category', 'feature', 'status', 'shopify_sync']
    search_fields = ['name', 'description', 'shopify_global_id']

    def save_model(self, request, obj, form, change):
        @receiver(sync_message)
        def add_sync_message(sender, level=messages.INFO, message='Contact your Shopify Partner for assistance.', **kwargs):
            """Signal handler to add message when shop sync error occurs"""
            messages.add_message(request, level, message)
        super(ProductAdmin, self).save_model(request, obj, form, change)

admin.site.register(ProductCategory)
admin.site.register(Color)