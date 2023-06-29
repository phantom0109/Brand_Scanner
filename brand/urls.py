from django.urls import path

from . import views

app_name = "brand"

urlpatterns = [
    path("", views.brand_listing, name="brand_listing"),
]
