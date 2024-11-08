from django.contrib import admin
from .models import Product, ProductImage, Color, ProductCategory
from apps.shopify_app.decorators import shopify_token_required


class MediaUploadInline(admin.StackedInline):
    model = ProductImage
    extra = 1
    max_num = 4

class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ("shop_GID", "created_at", "modified_at")

    fieldsets = [
        (None, {"fields": ["name", "category", "description", "primary_color"]}),
        ("Website Options", {"fields": ["display"]}),
        ("Storefront", {"fields": ["shop_sync", "shop_GID","shop_status","price","sku"]}),
        ("Technical Data", {"fields": ["created_at", "modified_at"]})
    ]
    inlines = [MediaUploadInline]
    list_display = ["name", "primary_color", "display", "shop_sync", "shop_GID", "shop_status"]
    list_filter = ["category", "display", "shop_sync"]
    search_fields = ["description"]

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCategory)
admin.site.register(Color)