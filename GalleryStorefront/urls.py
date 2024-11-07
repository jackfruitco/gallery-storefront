"""
URL configuration for GalleryStorefront project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.main, name='main')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='main')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from apps.main import views as main_views
from apps.shopify_app.decorators import shop_login_required

urlpatterns = [
    path('', main_views.index, name='index_redirect'),
    path('admin/', admin.site.urls, name='admin'),
    path('main/', include('apps.main.urls')),
    path('gallery/', include('apps.gallery.urls')),
    path('store/', include('apps.store.urls')),
    path('shopify/', include('apps.shopify_app.urls', namespace='shopify')),
]

if settings.DEBUG:  # new
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
