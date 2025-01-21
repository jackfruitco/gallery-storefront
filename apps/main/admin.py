import os

from django.contrib import admin

site_name = os.getenv("SITE_NAME", "Gallery Storefront Default")

admin.AdminSite.site_title = site_name
admin.AdminSite.site_header = site_name
