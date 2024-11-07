from . import views
from django.urls import path

app_name = "main"

urlpatterns = [
    path("", views.index, name="index"),
    # path("<slug>/about", views.AboutView.as_view(), name="about"),
    ]