from autoslug import AutoSlugField
from django.db import models


def _get_image_path(instance, filename):
    """Returns constructed file path for media"""
    return "images/SiteMedia/{0}".format(instance.slug + "." + filename.split(".")[-1])


class SiteMedia(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    description = models.CharField(
        max_length=100, blank=False, help_text="3-5 words describing the image"
    )
    slug = AutoSlugField(
        populate_from="description", unique_with="fk_product", always_update=True
    )
    image = models.ImageField(upload_to=_get_image_path)
