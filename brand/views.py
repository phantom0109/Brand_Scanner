from django.shortcuts import render


def brand_listing(request):
    return render(request, "brand-listing.html")
