from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from brand.models import Brand, Category, Tag

PAGE_SIZE = 20
BRAND_TAGS = {
    "location": Brand.Location.choices,
    "pricing": Brand.IndicativePricing.choices,
}


def home_page(request):
    return render(request, "index.html")


def brand_listing(request, selected_category):
    category = get_object_or_404(Category, internal_name=selected_category)

    tags = Tag.objects.filter(category__internal_name=category.internal_name)
    tag_names = set(tags.values_list("name", flat=True))

    # For filter options
    category_tags = dict()
    for tag in tags:
        if tag.name not in category_tags:
            category_tags[tag.name] = list()
        category_tags[tag.name].append(tag.value)

    # Get tags to filter brands based on query params
    query_filter = None
    for tag_name in tag_names:
        tag_values = request.GET.getlist(tag_name)

        for tag_value in tag_values:
            if query_filter is None:
                query_filter = Q(name=tag_name, value=tag_value)
            else:
                query_filter |= Q(name=tag_name, value=tag_value)

    if query_filter is not None:
        tags = tags.filter(query_filter)

    brands = None
    if query_filter is not None:
        # Filter brands
        brands = (
            Brand.objects.filter(brandtag__tag__in=tags)
            .annotate(match_count=Count("brandtag"))
            .filter(match_count=tags.count())
        )
    else:
        # Return all brands if no filter is applied
        brands = Brand.objects.filter(
            brandcategory__category__internal_name=category.internal_name
        )

    paginator = Paginator(brands, PAGE_SIZE)
    page_number = request.GET.get("page", 0)
    page = paginator.get_page(page_number)

    return render(
        request,
        "brand-listing.html",
        {
            "selected_category": category,
            "brands": page,
            "total_brands": len(brands),
            "category_tags": category_tags,
            "brand_tags": BRAND_TAGS,
        },
    )


def brand_detail(request, brand_id):
    brand = get_object_or_404(Brand, id=brand_id)
    return render(request, "brand-detail.html", {"brand": brand})
