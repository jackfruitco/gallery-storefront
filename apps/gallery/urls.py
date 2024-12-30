from . import views
from django.urls import path

app_name = "gallery"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<str:category>/<slug:slug>", views.DetailView.as_view(), name="product-detail"),
]
