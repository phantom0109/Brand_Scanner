from django.core.management.base import BaseCommand

from brand.models import Category, OnlineStore, Tag

valid_tag_names = [
    "type",
    "identity",
    "design",
    "occasion",
    "material",
]

category__tags = {
    "clothing": {
        "display_name": "Clothing",
        "tags": {
            "type": [
                "Fabrics",
                "Topwear",
                "Bottomwear",
                "Full body wear",
                "Innerwear",
                "Maternity wear",
                "Accessories",
            ],
            "identity": [
                "Men",
                "Women",
                "Unisex",
            ],
            "design": ["Ethnic", "Non-ethnic"],
            "occasion": [
                "Casual",
                "Work",
                "Party",
                "Active",
                "Home",
                "Sleep",
                "Wedding",
                "Beach",
            ],
            "material": ["Natural", "Synthetic"],
        },
    },
    "footwear": {
        "display_name": "Footwear",
        "tags": {
            "type": [
                "Flats",
                "Heels",
                "Boots",
                "Floaters",
                "Shoes",
            ],
            "identity": [
                "Men",
                "Women",
                "Unisex",
            ],
            "design": ["Ethnic", "Non-ethnic"],
            "occasion": [
                "Casual",
                "Work",
                "Party",
                "Active",
                "Travel",
                "Wedding",
                "Beach",
            ],
            "material": ["Natural", "Synthetic"],
        },
    },
    "handbags": {
        "display_name": "Handbags",
        "tags": {
            "type": [
                "Small",
                "Medium",
                "Large",
            ],
            "identity": [
                "Men",
                "Women",
                "Unisex",
            ],
            "design": [
                "Classic",
                "Abstract",
                "Brand styles",
                "Ethnic",
                "Textured",
                "Others",
            ],
            "occasion": [
                "Casual",
                "Work",
                "Party",
                "Active",
                "Travel",
                "Wedding",
            ],
        },
    },
    "jewellery": {
        "display_name": "Jewellery",
        "tags": {
            "type": [
                "Hair",
                "Ears",
                "Neck",
                "Hands",
                "Feet",
                "Others",
            ],
            "identity": [
                "Men",
                "Women",
                "Unisex",
            ],
            "design": [
                "Classic",
                "Abstract",
                "Brand styles",
                "Ethnic",
                "Textured",
                "Others",
            ],
            "occasion": [
                "Casual",
                "Work",
                "Party",
                "Active",
                "Travel",
                "Wedding",
            ],
        },
    },
    "wellness": {
        "display_name": "Beauty & Wellness",
        "tags": {
            "type": [
                "Make-up",
                "Skin",
                "Hair",
                "Bath & Body",
                "Mom & Baby",
                "Fragrance",
            ],
            "identity": [
                "Men",
                "Women",
                "Unisex",
            ],
        },
    },
    "kids": {
        "display_name": "Baby & Kids",
        "tags": {
            "type": [
                "Clothing",
                "Footwear",
                "Jewellery",
                "Body & Bath",
                "Nursery",
                "Essentials",
                "Books & Toys",
                "Others",
            ],
            "identity": [
                "Men",
                "Women",
                "Unisex",
            ],
        },
    },
    "food": {
        "display_name": "Food & Health",
        "tags": {
            "type": [
                "Snacks & Instant Food",
                "Breakfast Food",
                "Beverages",
                "Spreads & Sauces",
                "Dairy & Bakery",
                "Protein Supplements",
                "Desserts",
            ]
        },
    },
    "home": {
        "display_name": "Home & Kitchen",
        "tags": {
            "type": [
                "Living & Decor",
                "Kitchen & Dining",
                "Garden & Outdoors",
                "Home Improvement & Tools",
                "Stationary & Organisers",
                "Bedspreads, Cusions, & Others",
            ]
        },
    },
    "gifting": {
        "display_name": "Gifting",
        "tags": {
            "type": [
                "Food & Health",
                "Home Decor",
                "Jewellery",
                "Beauty & Wellness",
                "Others",
            ],
            "occasion": [
                "Birthday",
                "Anniversary",
                "Wedding & Engagement",
                "Best Wishes",
                "Corporate Gifting",
            ],
        },
    },
    "pets": {
        "display_name": "Pet Supplies",
        "tags": {
            "type": [
                "Food & Bowls",
                "Health & Hygiene",
                "Travel & Walk Essentials",
                "Clothing & Accessories",
                "Toys",
                "Others",
            ],
            "identity": [
                "Dogs",
                "Cats",
                "Fish & Aquatic Animals",
                "Birds",
                "Others",
            ],
        },
    },
}

online_stores = [
    "Ajio",
    "Amazon",
    "Filpkart",
    "FirstCry",
    "Myntra",
    "Nykaa",
]


def populate_category_tags(category, tags):
    for tag_name in tags:
        if tag_name not in valid_tag_names:
            print(f"Invalid tag name {tag_name}.")
            continue

        for tag_value in tags[tag_name]:
            (tag, created) = Tag.objects.get_or_create(
                category=category, name=tag_name, value=tag_value
            )
            if created:
                print(f"Added tag {tag}")


def populate_online_stores(stores):
    for store_name in stores:
        (store, created) = OnlineStore.objects.get_or_create(name=store_name)

        if created:
            print(f"Added online store {store_name}")


class Command(BaseCommand):
    help = "Populates fields for internal models."

    def handle(self, *args, **options):
        for category_internal_name in category__tags:
            (category, created) = Category.objects.get_or_create(
                internal_name=category_internal_name,
                display_name=category__tags[category_internal_name][
                    "display_name"
                ],
            )
            if created:
                print(f"Added category {category}")

            populate_category_tags(
                category, category__tags[category.internal_name]["tags"]
            )

        populate_online_stores(online_stores)
