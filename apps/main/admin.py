from django.contrib import admin
# from .models import Profile , Contact

site_name = 'Pottery By Marnie'

# class ChoiceInline(admin.StackedInline):
#    model = Contact
#    extra = 1

# class ProfileAdmin(admin.ModelAdmin):
#    fieldsets = [
#         ("Profile Name", {"fields": ["first_name", "middle_name", "last_name", ]}),
#         ("About Me", {"fields": ["quote", "about_me"]}),
#         ("Profile Data", {"fields": ["position", "active", "display_on_home", "portrait", "user", "slug"]}),
#    ]
#    # inlines = [ChoiceInline]
#    list_display = ["last_name", "first_name", "middle_name"]
#    list_filter = ["position", "active", "display_on_home"]
#    search_fields = ["last_name", "first_name"]


# admin.site.register(Profile, ProfileAdmin)
#
admin.AdminSite.site_title = site_name
admin.AdminSite.site_header = site_name



