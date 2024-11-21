from django.contrib import admin
from .models import ShopifyAccessToken


@admin.register(ShopifyAccessToken)
class ShopifyAccessToken(admin.ModelAdmin):
    readonly_fields = ("user", "access_token", "created_at")

    fieldsets = [
        (None, {"fields": ["user", "access_token", "created_at"]}),
    ]