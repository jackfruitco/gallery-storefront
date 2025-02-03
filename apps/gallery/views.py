from django.shortcuts import render
from django.views import generic
from django.views.decorators.http import require_http_methods

from .models import Product, ProductCategory


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
    return render(request, "gallery/index.html", {"products": products, "categories": categories})

class DetailView(generic.DetailView):
    template_name = "gallery/detail.html"
    model = Product

@require_http_methods(["GET"])
def carousel_filter(request, category):
    products = Product.objects.filter(category__name=category).order_by("-created_at")
    return render(request, "gallery/product-carousel.html", {"products": products})
