from django.contrib import admin
from .models import Product, ProductImage, Color, ProductCategory


class MediaUploadInline(admin.StackedInline):
    model = ProductImage
    extra = 1
    max_num = 4

class ProductAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["name", "category", "description", "primary_color"]}),
        ("Website Options", {"fields": ["display"]}),
        ("Storefront", {"fields": ["add_to_shopify", "shop_GID","price","sku"]}),
    ]
    inlines = [MediaUploadInline]
    list_display = ["name", "primary_color", "display"]
    list_filter = ["category", "display"]
    search_fields = ["description"]

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCategory)
admin.site.register(Color)