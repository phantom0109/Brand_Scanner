from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "brand"

urlpatterns = [
    path("", RedirectView.as_view(url="clothing/")),
    path("p/", RedirectView.as_view(url="../clothing/")),
    path("p/<int:brand_id>/", views.brand_detail, name="brand_detail"),
    path(
        "<str:selected_category>/", views.brand_listing, name="brand_listing"
    ),
]
