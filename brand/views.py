from django.shortcuts import render

from brand.models import Brand, Category, Tag

BRAND_TAGS = {
    "location": Brand.Location.choices,
    "indicative_pricing": Brand.IndicativePricing.choices,
}


def home_page(request):
    return render(request, "index.html")


def brand_listing(request, selected_category):
    category = Category.objects.get(internal_name=selected_category)

    brands = Brand.objects.filter(
        brandcategory__category__internal_name=category.internal_name
    )
    tags = Tag.objects.filter(category__internal_name=category.internal_name)

    category_tags = dict()
    for tag in tags:
        if tag.name not in category_tags:
            category_tags[tag.name] = list()
        category_tags[tag.name].append(tag.value)

    return render(
        request,
        "brand-listing.html",
        {
            "selected_category": category,
            "brands": brands,
            "category_tags": category_tags,
            "brand_tags": BRAND_TAGS,
        },
    )
