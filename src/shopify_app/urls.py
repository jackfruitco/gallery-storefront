from django.urls import path

from . import views

app_name = "shopify"
urlpatterns = [
    path("login", views.login, name="login"),
    path("authenticate", views.authenticate, name="shopify_app_authenticate"),
    path("finalize", views.finalize, name="finalize"),
    path("logout", views.logout, name="shopify_app_logout"),
]
