from django.shortcuts import render

from brand.models import Brand


def brand_listing(request):
    brands = Brand.objects.filter()
    return render(request, "brand-listing.html", {"brands": brands})
