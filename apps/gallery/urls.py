from . import views
from django.urls import path

app_name = "gallery"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>", views.DetailView.as_view(), name="detail"),
]
