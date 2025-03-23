from django.shortcuts import render
from django.views import generic
from django.views.decorators.http import require_http_methods

from gallery.models import Product


class StoreListView(generic.ListView):
    template_name = "store/index.html"
    context_object_name = "products"

    def get_queryset(self):
        """Return the last 16 published products."""
        return Product.objects.filter(status="ACTIVE").order_by("-created_at")


@require_http_methods(["DELETE"])
def store_delete(request, id):
    Product.objects.get(id=id).delete()
    products = Product.objects.all()
    return render(request, "store/display_products.html", {"products": products})
