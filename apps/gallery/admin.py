from django.contrib import admin, messages
from django.dispatch import receiver
from apps.shopify_app.signals import shop_sync_error
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
        @receiver(shop_sync_error)
        def add_sync_error_message(sender, response='unknown', publication='unknown', **kwargs):
            """Signal handler to add message when shop sync error occurs"""
            message = ("The product %s failed to publish to Shopify %s (%s). Contact your Shopify Partner." %
                       (obj.name, publication, response))
            messages.warning(request, message)

        super(ProductAdmin, self).save_model(request, obj, form, change)
        if obj.sync_error or (obj.shop_sync and not obj.shop_global_id):
            data  = {"lvl": messages.ERROR,
                     "msg": 'The product "%s" did not sync to Shopify successfully (%s).' % (
                     obj.name, obj.sync_error_msg)}
        elif not obj.sync_error and obj.shop_sync:
            data  = {"lvl": messages.SUCCESS,
                     "msg": 'The product "%s" was synced successfully with Shopify in %s status.' % (
                     obj.name, obj.shop_status)}
        else: data = None
        if data is not None: messages.add_message(request, data["lvl"], data["msg"])

    #def delete_model(self, request, obj):
    #    if obj.shop_sync: flag_for_removal = True
    #    super(ProductAdmin, self).delete_model(request, obj)
    #    if flag_for_removal:

admin.site.register(ProductCategory)
admin.site.register(Color)