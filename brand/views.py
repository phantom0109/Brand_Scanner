import copy

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from brand.models import Brand, Category, Tag

PAGE_SIZE = 20
BRAND_TAGS = {
    # Keys are model field names
    "location": [
        {"value": item[0], "display_name": item[1]}
        for item in Brand.Location.choices
    ],
    "indicative_pricing": [
        {"value": item[0], "display_name": item[1]}
        for item in Brand.IndicativePricing.choices
    ],
}


def _update_display_tags(category_tags, tag_name, tag_value, update_fields):
    for option in category_tags[tag_name]:
        if option["value"] == tag_value:
            for field in update_fields:
                option[field] = update_fields[field]


def home_page(request):
    return render(request, "index.html")


def brand_listing(request, selected_category):
    category = get_object_or_404(Category, internal_name=selected_category)

    tags = Tag.objects.filter(category__internal_name=category.internal_name)
    category_tag_names = set(tags.values_list("name", flat=True))

    # For filter options
    category_tags = dict()
    for tag in tags:
        if tag.name not in category_tags:
            category_tags[tag.name] = list()
        category_tags[tag.name].append({"value": tag.value})

    # Filter brands based on category tags provided in request params
    query_filter = None
    for tag_name in category_tag_names:
        tag_values = request.GET.getlist(tag_name)

        for tag_value in tag_values:
            if query_filter is None:
                query_filter = Q(name=tag_name, value=tag_value)
            else:
                query_filter |= Q(name=tag_name, value=tag_value)

            _update_display_tags(
                category_tags, tag_name, tag_value, {"selected": True}
            )

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

    # Further filter brands based on brand tags provided in request params
    brand_tags = copy.deepcopy(BRAND_TAGS)
    brand_tag_names = brand_tags.keys()
    for tag_name in brand_tag_names:
        tag_values = request.GET.getlist(tag_name)

        query_filter = None
        for tag_value in tag_values:
            if query_filter is None:
                query_filter = Q(**{f"{tag_name}": tag_value})
            else:
                query_filter |= Q(**{f"{tag_name}": tag_value})

            _update_display_tags(
                brand_tags, tag_name, tag_value, {"selected": True}
            )

        if query_filter is not None:
            brands = brands.filter(query_filter)

    paginator = Paginator(brands, PAGE_SIZE)
    page_number = request.GET.get("page", 0)
    page = paginator.get_page(page_number)

    print(brand_tags)
    return render(
        request,
        "brand-listing.html",
        {
            "selected_category": category,
            "brands": page,
            "total_brands": len(brands),
            "category_tags": category_tags,
            "brand_tags": brand_tags,
        },
    )


def brand_detail(request, brand_id):
    brand = get_object_or_404(Brand, id=brand_id)
    return render(request, "brand-detail.html", {"brand": brand})
