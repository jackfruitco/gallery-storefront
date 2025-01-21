from django.urls import path

from .views import StoreListView, store_delete

app_name = "store"
urlpatterns = [
    path("", StoreListView.as_view(), name="index"),
    path("<int:id>/delete", store_delete, name="delete"),
]
