from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include
from django.urls import path

from gallery.sitemaps import ProductSitemap
from main import views as MainViews

sitemaps = {
    "products": ProductSitemap,
}
urlpatterns = [
    path("", MainViews.index, name="index"),
    path("admin/", admin.site.urls, name="admin"),
    path("main/", include("main.urls")),
    path("gallery/", include("gallery.urls")),
    path("store/", include("store.urls")),
    path("shopify/", include("shopify_app.urls", namespace="shopify")),
    path(
        "robots.txt",
        MainViews.RobotsView.as_view(content_type="text/plain"),
        name="robots",
    ),
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
