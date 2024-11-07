from . import views
from django.urls import path

app_name = "shopify"
urlpatterns = [
    path('login', views.login, name='login'),
    path('authenticate', views.authenticate, name='shopify_app_authenticate'),
    path('finalize', views.finalize, name='finalize'),
    path('logout', views.logout, name='shopify_app_logout'),
    path("sync-error", views.sync_error, name="sync_error"),
    path("sync-debug", views.sync_success, name="sync_debug"),
    ]