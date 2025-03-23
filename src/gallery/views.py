import logging

from django.shortcuts import render
from django.views import generic
from django.views.decorators.http import require_http_methods

from .models import Product
from .models import ProductCategory

logger = logging.getLogger(__name__)

# Create your views here.

# class IndexView(generic.ListView):
#     template_name = "gallery/index.html"
#     context_object_name = "product_list"
#
#     def get_queryset(self):
#         """Return the last 16 published products."""
#         return Product.objects.filter(status="ACTIVE").order_by("-created_at")[:16]


def IndexView(request):
    products = Product.objects.filter(status="ACTIVE").order_by("-created_at")[:16]
    categories = ProductCategory.objects.all()
    return render(
        request, "gallery/index.html", {"products": products, "categories": categories}
    )


class DetailView(generic.DetailView):
    template_name = "gallery/detail.html"
    model = Product


@require_http_methods(["GET"])
def carousel_filter(request):
    # Retrieve filters from request
    filters = request.GET.getlist("filters", default=[])

    # Set QuerySet to all products initially
    products = Product.objects.filter(status="ACTIVE").order_by("-created_at")

    # Apply filter if filters found in request
    if filters:
        products = products.filter(category__name__in=filters).order_by("-created_at")

    return render(
        request,
        "gallery/product-carousel.html",
        {"products": products, "filters": filters},
    )
