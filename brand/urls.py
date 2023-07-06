from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "brand"

urlpatterns = [
    path("", RedirectView.as_view(url="clothing/")),
    path(
        "<str:selected_category>/", views.brand_listing, name="brand_listing"
    ),
]
