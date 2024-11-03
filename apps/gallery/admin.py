from django.contrib import admin
from .models import Project, ProjectImage, ProjectType, Color


class MediaUploadInline(admin.StackedInline):
    model = ProjectImage
    extra = 1
    max_num = 4

class ProjectAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["name", "type", "description", "primary_color"]}),
        ("Website Options", {"fields": ["display"]}),
        ("Storefront", {"fields": []}),
    ]
    inlines = [MediaUploadInline]
    list_display = ["name", "primary_color", "display"]
    list_filter = ["type", "display"]
    search_fields = ["description"]

admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectType)
admin.site.register(Color)