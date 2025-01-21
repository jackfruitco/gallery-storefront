from django.urls import path

from . import views

app_name = "gallery"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path(
        "<str:category>/<slug:slug>", views.DetailView.as_view(), name="product-detail"
    ),
]
