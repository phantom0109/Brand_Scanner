from django.shortcuts import render

from brand.models import Brand, Category, Tag

BRAND_TAGS = {
    "location": Brand.Location.choices,
    "indicative_pricing": Brand.IndicativePricing.choices,
}


def home_page(request):
    return render(request, "index.html")


def brand_listing(request):
    selected_category = "Footwear"

    category = Category.objects.get(name=selected_category)

    brands = Brand.objects.filter(brandcategory__category__name=category.name)
    tags = Tag.objects.filter(category__name=category.name)

    category_tags = dict()
    for tag in tags:
        if tag.name not in category_tags:
            category_tags[tag.name] = list()
        category_tags[tag.name].append(tag.value)

    return render(
        request,
        "brand-listing.html",
        {
            "brands": brands,
            "category_tags": category_tags,
            "brand_tags": BRAND_TAGS,
        },
    )
