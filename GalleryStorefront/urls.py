from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.gallery.sitemaps import ProductSitemap
from apps.main import views as main_views

sitemaps = {
    "products": ProductSitemap,
}
urlpatterns = [
    path("", main_views.index, name="index_redirect"),
    path("admin/", admin.site.urls, name="admin"),
    path("main/", include("apps.main.urls")),
    path("gallery/", include("apps.gallery.urls")),
    path("store/", include("apps.store.urls")),
    path("shopify/", include("apps.shopify_app.urls", namespace="shopify")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

if settings.DEBUG:  # new
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
