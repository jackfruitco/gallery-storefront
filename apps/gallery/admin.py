from django.contrib import messages
from django.contrib import admin
from .models import Product, ProductImage, Color, ProductCategory
from apps.shopify_app.decorators import shopify_token_required


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
        super(ProductAdmin, self).save_model(request, obj, form, change)
        if obj.shop_global_id:
            msg = 'The product "%s" was synced successfully with Shopify in %s status.' % (obj.name, obj.shop_status)
            messages.add_message(request, messages.INFO, msg)

# admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCategory)
admin.site.register(Color)