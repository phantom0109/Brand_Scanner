from django.core.management.base import BaseCommand

from brand.models import (
    Brand,
    BrandCategory,
    BrandKeyPerson,
    BrandOnlineStore,
    BrandTag,
    BrandVisual,
    Category,
    Person,
)
from utilities.converters import csv_to_dict_list
from utilities.imports import (
    CHECK_IF_EXISTING,
    import_as_brand,
    import_as_brandcategory,
    import_as_brandkeyperson,
    import_as_brandonlinestore,
    import_as_brandtag,
    import_as_brandvisual,
    import_as_person,
    import_remaining_brandassets,
)
from utilities.validators import is_csv

FOOTWEAR_RULES = {
    "Brand": {
        "pre": {"must": ["name"]},
        "fields": {
            # Basic
            "name": {
                "type": "text",
                "source": "Name of Brand",
                "must": True,
            },
            "title": {
                "type": "text",
                "source": "Title of Brand",
                "default": "UNKNOWN",
            },
            "description": {
                "type": "text",
                "source": "Brand Info (less than 100 words)",
                "default": "UNKNOWN",
            },
            "founding_year": {
                "type": "number",
                "source": "founded_in_year_cleaned",
                "default": 2020,
            },
            "company_size": {
                "type": "number",
                "source": "Company Size",
                "default": 1,
            },
            "location": {
                "type": "enum",
                "source": "Brand Location",
                "choices": {
                    "India": Brand.Location.INDIA,
                    "International": Brand.Location.INTERNATIONAL,
                },
                "default": Brand.Location.INDIA,
            },
            # Shopping
            "offline_presence": {
                "type": "enum",
                "source": "Available on offline stores",
                "choices": {
                    "Yes": True,
                    "No": False,
                },
                "default": False,
            },
            "delivery_days": {
                "type": "number",
                "source": "Delivery (in days)",
                "default": 7,
            },
            "return_days": {
                "type": "number",
                "source": "Returns ( In days)",
                "default": 7,
            },
            "payment_mode": {
                "type": "enum",
                "source": "Payment",
                "choices": {
                    "Prepaid": Brand.PaymentMode.PREPAID_ONLY,
                    "Payment on Delivery": Brand.PaymentMode.BOTH,
                },
            },
            "refund_mode": {
                "type": "enum",
                "source": "Refund",
                "choices": {
                    "Exchange only": Brand.RefundMode.EXCHANGE_ONLY,
                    "Not Applicable": Brand.RefundMode.NA,
                },
            },
            # Communication
            "website": {
                "type": "text",
                "source": "Website",
                "default": "https://thebrandscanner.in",
            },
            "phone_number": {
                "type": "text",
                "source": "phone_number_cleaned",
                "default": "UNKNOWN",
            },
            "email_address": {
                "type": "text",
                "source": "Email Id",
                "default": "thebrandscanner@gmail.com",
            },
            "instagram_profile": {
                "type": "text",
                "source": "Instagram url",
            },
            "facebook_profile": {
                "type": "text",
                "source": "Facebook url",
            },
            # Labels
            "indicative_pricing": {
                "type": "enum",
                "source": "indicative_pricing_cleaned",
                "choices": {
                    "100": Brand.IndicativePricing.BUDGET_FRIENDLY,
                    "1000": Brand.IndicativePricing.VALUE,
                    "10000": Brand.IndicativePricing.LUXURY,
                },
            },
            "made_in_india": {
                "type": "enum",
                "source": "Made in India",
                "choices": {"Yes": True, "No": False},
            },
            "environment_friendly": {
                "type": "multiple_choice",
                "source": "Adhoc Questions",
                "contains": {
                    "Sustainable": True,
                },
            },
            "handcrafted": {
                "type": "multiple_choice",
                "source": "Adhoc Questions",
                "contains": {
                    "Handcrafted": True,
                },
            },
            "customizable": {
                "type": "multiple_choice",
                "source": "Adhoc Questions",
                "contains": {
                    "Customizable": True,
                },
            },
            "material": {
                "type": "text",
                "source": "Material Text",
            },
        },
    },
    "BrandOnlineStore": {
        "pre": {
            "foreign": {
                "accept": ["Brand"],
                "filter_multiple": {
                    "OnlineStore": [
                        {"source": {"name": "Available on online stores"}},
                    ]
                },
            }
        },
        "fields": {
            "brand": {
                "type": "FK",
                "model": "Brand",
            },
            "online_store": {
                "type": "FK",
                "model": "OnlineStore",
            },
        },
    },
    "Person": {
        "pre": {
            "must": ["name"],
            "image_download": ["photo"],
        },
        "fields": {
            "salutation": {
                "type": "enum",
                "source": "Salutation",
                "choices": {
                    "Mr.": Person.Salutation.MR,
                    "Ms.": Person.Salutation.MS,
                    "Mrs.": Person.Salutation.MRS,
                    "DR.": Person.Salutation.DR,
                    "Pt.": Person.Salutation.PT,
                },
            },
            "name": {
                "type": "text",
                "source": "Name of Founder",
            },
            "photo": {
                "type": "image",
                "source": "Photo of Founder (url)",
            },
            "background": {
                "type": "text",
                "source": "Background of Founder",
            },
        },
    },
    "BrandKeyPerson": {
        "pre": {
            "foreign": {
                "accept": ["Brand", "Person"],
            }
        },
        "fields": {
            "brand": {"type": "FK", "model": "Brand"},
            "person": {"type": "FK", "model": "Person"},
            "designation": {"type": "OVERRIDE", "value": "FR"},
        },
    },
    "BrandAsset": {
        "pre": {
            "must": ["asset"],
            "foreign": {"accept": ["Brand"]},
            "image_download": ["asset"],
        },
        "fields": {
            "brand": {
                "type": "FK",
                "model": "Brand",
            },
            "asset": {
                "type": "image",
            },
            "title": {
                "type": "text",
            },
        },
    },
    "BrandVisual": {
        "pre": {
            "foreign": {
                "accept": ["Brand"],
                "create": {
                    "logo": {
                        "model": "BrandAsset",
                        "supply": {
                            "asset": {"source": "Logo"},
                            "title": {"static": "Logo"},
                        },
                    },
                    "cover": {
                        "model": "BrandAsset",
                        "supply": {
                            "asset": {"source": "Brand Image"},
                            "title": {"static": "Cover Image"},
                        },
                    },
                },
            }
        },
        "fields": {
            "brand": {
                "type": "FK",
                "model": "Brand",
            },
            "logo": {"type": "FK", "model": "BrandAsset__logo"},
            "cover": {"type": "FK", "model": "BrandAsset__cover"},
        },
    },
    "BrandCategory": {
        "pre": {"foreign": {"accept": ["Brand", "Category"]}},
        "fields": {
            "brand": {
                "type": "FK",
                "model": "Brand",
            },
            "category": {"type": "FK", "model": "Category"},
        },
    },
    "BrandTag": {
        "pre": {
            "foreign": {
                "accept": ["Brand", "Category"],
                "filter_multiple": {
                    "Tag": [
                        {
                            "static": {"name": "identity"},
                            "source": {"value": "Identity"},
                            "foreign": {"category": "Category"},
                        },
                        {
                            "static": {"name": "type"},
                            "source": {"value": "Type"},
                            "foreign": {"category": "Category"},
                        },
                        {
                            "static": {"name": "material"},
                            "source": {"value": "Material"},
                            "foreign": {"category": "Category"},
                        },
                        {
                            "static": {"name": "design"},
                            "source": {"value": "Design"},
                            "foreign": {"category": "Category"},
                        },
                        {
                            "static": {"name": "occasion"},
                            "source": {"value": "Occasion"},
                            "foreign": {"category": "Category"},
                        },
                    ]
                },
            },
            "replace": {
                "Identity": {
                    "He/ Him": "Men",
                    "She/ Her": "Women",
                },
                "Type": {"Heals": "Heels"},
            },
        },
        "fields": {
            "brand": {"type": "FK", "model": "Brand"},
            "tag": {"type": "FK", "model": "Tag"},
        },
    },
}


CATEGORY__RULES = {"footwear": FOOTWEAR_RULES}


class Command(BaseCommand):
    help = "Imports food and health data"

    def add_arguments(self, parser):
        parser.add_argument("--csv", type=str)

    def handle(self, *args, **options):
        csv_file_path = options["csv"]

        if not is_csv(csv_file_path):
            print(f"{csv_file_path} is not a CSV file.")

        category = Category.objects.get_or_create(internal_name="footwear")[0]
        print(f"Category is {category}")

        csv_rows = csv_to_dict_list(csv_file_path)[:3]
        for idx, csv_row in enumerate(csv_rows):
            print(f"\n==== Reading row entry at idx {idx} ====")

            # Import Brand
            print(">> Brand <<")
            brand = import_as_brand(
                CATEGORY__RULES[category.internal_name], csv_row
            )
            if brand is None:
                print("Ignored Brand. Skipping other model imports as well.")
                continue

            if Brand.objects.filter(name=brand.name).exists():
                brand = Brand.objects.get(name=brand.name)
                print(f"Using existing brand {brand}")
            else:
                brand.full_clean()
                brand.save()
                print(f"Created entry {brand}")

            # Import BrandOnlineStore
            print(">> BrandOnlineStore <<")
            brand_online_stores = import_as_brandonlinestore(
                CATEGORY__RULES[category.internal_name],
                csv_row,
                foreign={"Brand": brand},
            )
            for brand_online_store in brand_online_stores:
                if not BrandOnlineStore.objects.filter(
                    brand=brand_online_store.brand,
                    online_store=brand_online_store.online_store,
                ).exists():
                    brand_online_store.full_clean()
                    brand_online_store.save()
                    print(f"Created entry {brand_online_store}.")
                else:
                    print(f"{brand_online_store} already exists. Skipping.")

            # Import Person
            print(">> Person <<")
            person = import_as_person(
                CATEGORY__RULES[category.internal_name], csv_row
            )
            import_brandkeyperson = False
            if person is None:
                print("Ignored Person.")
            elif Person.objects.filter(name=person.name).exists():
                person = Person.objects.get(name=person.name)
                print(f"Using existing person {person}.")
                import_brandkeyperson = True
            else:
                person.full_clean()
                person.save()
                import_brandkeyperson = True
                print(f"Created entry {person}")

            # Import BrandKeyPerson with FK to Brand and Person
            if import_brandkeyperson:
                print(">> BrandKeyPerson <<")
                brand_key_person = import_as_brandkeyperson(
                    CATEGORY__RULES[category.internal_name],
                    csv_row,
                    foreign={"Brand": brand, "Person": person},
                )
                if not BrandKeyPerson.objects.filter(
                    brand=brand_key_person.brand,
                    person=brand_key_person.person,
                ).exists():
                    brand_key_person.full_clean()
                    brand_key_person.save()
                    print(f"Created entry {brand_key_person}")
                else:
                    print(f"{brand_key_person} already exists. Skipping.")

            # Import BrandVisual and corresponding BrandAsset
            print(">> BrandVisual <<")
            brand_visual = import_as_brandvisual(
                CATEGORY__RULES[category.internal_name],
                csv_row,
                foreign={"Brand": brand},
            )
            if not BrandVisual.objects.filter(
                brand=brand_visual.brand
            ).exists():
                brand_visual.full_clean()
                brand_visual.save()
                print(f"Created entry {brand_visual}")
            else:
                print(f"{brand_visual} already exists. Skipping.")

            # Import remaining BrandAsset
            print(">> Other BrandAsset <<")
            brand_assets = import_remaining_brandassets(
                CATEGORY__RULES[category.internal_name],
                csv_row,
                foreign={"Brand": brand},
            )
            for brand_asset in brand_assets:
                if not CHECK_IF_EXISTING["BrandAsset"](brand_asset):
                    brand_asset.full_clean()
                    brand_asset.save()
                    print(f"Created entry {brand_asset}")

            # Import BrandCategory
            print(">> BrandCategory <<")
            brand_category = import_as_brandcategory(
                CATEGORY__RULES[category.internal_name],
                csv_row,
                foreign={"Brand": brand, "Category": category},
            )
            if not BrandCategory.objects.filter(
                brand=brand, category=category
            ).exists():
                brand_category.full_clean()
                brand_category.save()
                print(f"Created entry {brand_category}")
            else:
                print(f"{brand_category} already exists. Skipping.")

            # Import BrandTag
            print(">> BrandTag <<")
            brand_tags = import_as_brandtag(
                CATEGORY__RULES[category.internal_name],
                csv_row,
                foreign={"Brand": brand, "Category": category},
            )
            for brand_tag in brand_tags:
                if not BrandTag.objects.filter(
                    brand=brand_tag.brand, tag=brand_tag.tag
                ).exists():
                    brand_tag.full_clean()
                    brand_tag.save()
                    print(f"Created entry {brand_tag}")
                else:
                    print(f"{brand_tag} already exists. Skipping.")
