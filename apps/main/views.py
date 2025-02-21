from django.shortcuts import render
from django.views.generic import TemplateView

from apps.gallery.models import Product


def index(request):
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get("num_visits", 0)
    num_visits += 1
    request.session["num_visits"] = num_visits

    products = (
        Product.objects.filter(status="ACTIVE")
        .filter(feature=True)
        .order_by("-created_at")[:4]
    )

    return render(
        request,
        "main/index.html",
        {"products": products},
    )


class RobotsView(TemplateView):
    template_name = "robots.txt"
