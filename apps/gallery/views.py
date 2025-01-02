# from django.db.models import F
# from django.http import HttpResponseRedirect
# from django.shortcuts import get_object_or_404, render
# from django.urls import reverse
from django.views import generic

from .models import Product, ProductImage


# Create your views here.
class IndexView(generic.ListView):
    template_name = "gallery/index.html"
    context_object_name = "product_list"

    def get_queryset(self):
        """Return the last 16 published products."""
        return Product.objects.filter(status='ACTIVE').order_by("-created_at")[:16]

class DetailView(generic.DetailView):
    template_name = "gallery/detail.html"
    model = Product