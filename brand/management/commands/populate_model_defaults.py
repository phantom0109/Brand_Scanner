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
    "Clothing": {
        "type": [
            "Fabrics",
            "Topwear",
            "Bottomwear",
            "Full body wear",
            "Innerwear",
            "Maternity wear",
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
    },
    "Footwear": {
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
    "Handbags": {
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
    "Jewellery": {
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
    "Beauty & Wellness": {
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
    "Baby & Kids": {
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
    "Food & Health": {
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
    "Home & Kitchen": {
        "type": [
            "Living & Decor",
            "Kitchen & Dining",
            "Garden & Outdoors",
            "Home Improvement & Tools",
            "Stationary & Organisers",
            "Bedspreads, Cusions, & Others",
        ]
    },
    "Gifting": {
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
    "Pet Supplies": {
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
        for category_name in category__tags:
            (category, created) = Category.objects.get_or_create(
                name=category_name
            )
            if created:
                print(f"Added category {category}")

            populate_category_tags(category, category__tags[category.name])

        populate_online_stores(online_stores)
