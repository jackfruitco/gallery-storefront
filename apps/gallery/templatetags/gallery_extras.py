import os

from django import template

from apps.gallery.models import Product

register = template.Library()


@register.filter(is_safe=True)
def get_ext(value):
    """Retrieves the extension of the given filename string."""
    file_name, file_ext = os.path.splitext(value)
    return file_ext


@register.filter(is_safe=True)
def get_all_product_images(product_pk):
    return Product.objects.filter(id=product_pk).all()
