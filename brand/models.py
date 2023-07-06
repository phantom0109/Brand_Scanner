from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower

from utilities.dates import current_india_time


class LowerCaseCharField(models.CharField):
    def get_prep_value(self, value):
        return str(value).lower()


class Brand(models.Model):
    class Location(models.TextChoices):
        INDIA = "IND"
        INTERNATIONAL = "INT"

    class PaymentMode(models.TextChoices):
        PREPAID_ONLY = "PRE", "Prepaid Only"
        BOTH = "BOTH", "Both Prepaid and Payment On Delivery"

    class RefundMode(models.TextChoices):
        REFUND = "RFND", "Can Refund Or Exchange"
        EXCHANGE_ONLY = "EXCH", "No Refund, Exchange Only"
        NA = "NONE", "Neither Refund Nor Exchange"

    class IndicativePricing(models.TextChoices):
        BUDGET_FRIENDLY = "BGT"
        VALUE = "VAL"
        LUXURY = "LUX"

    # Basic
    name = models.CharField(max_length=100)
    company_name = models.CharField(blank=True, max_length=100)
    title = models.CharField(max_length=300)
    description = models.TextField()
    founding_year = models.PositiveIntegerField(
        validators=[MinValueValidator(1500), MaxValueValidator(3000)]
    )
    company_size = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], default=1
    )
    location = models.CharField(max_length=3, choices=Location.choices)

    # Shopping
    offline_presence = models.BooleanField(default=False)
    delivery_days = models.PositiveIntegerField(default=7)
    return_days = models.PositiveIntegerField(default=7)
    payment_mode = models.CharField(
        max_length=4, blank=True, choices=PaymentMode.choices
    )
    refund_mode = models.CharField(
        max_length=4, blank=True, choices=RefundMode.choices
    )
    refund_shipping_included = models.BooleanField(default=False)

    # Communication
    company_address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email_address = models.EmailField(blank=True)
    instagram_profile = models.URLField(max_length=100, blank=True)
    facebook_profile = models.URLField(max_length=100, blank=True)
    linkedin_profile = models.URLField(max_length=100, blank=True)
    twitter_profile = models.URLField(max_length=100, blank=True)

    # Labels
    indicative_pricing = models.CharField(
        max_length=3, blank=True, choices=IndicativePricing.choices
    )
    made_in_india = models.BooleanField(default=True)
    environment_friendly = models.BooleanField(default=False)
    handcrafted = models.BooleanField(default=False)
    customizable = models.BooleanField(default=False)
    plus_size_available = models.BooleanField(default=False)
    material = models.CharField(max_length=250, blank=True)
    certifications = models.CharField(max_length=250, blank=True)

    # Others
    keywords = models.TextField(blank=True)
    is_claimed = models.BooleanField(default=False)
    user_rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
    )
    brandscanner_rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
    )
    page_views = models.PositiveIntegerField(default=0)

    # System internal
    last_updated = models.DateTimeField(default=current_india_time)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class OnlineStore(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower("name"), name="unique_case_insensitive_online_store_name"
            )
        ]


class BrandOnlineStore(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    online_store = models.ForeignKey(OnlineStore, on_delete=models.PROTECT)

    def __str__(self):
        return f"[{self.brand}] {self.online_store}"

    class Meta:
        constraints = [
            UniqueConstraint(
                "brand", "online_store", name="unique_brand_online_store_pair"
            )
        ]


class Person(models.Model):
    class Salutation(models.TextChoices):
        MR = "MR", "Mr."
        MS = "MS", "Ms."
        MRS = "MRS", "Mrs."
        DR = "DR", "Dr."
        PT = "PT", "Pt."

    salutation = models.CharField(max_length=4, choices=Salutation.choices)
    name = models.CharField(max_length=100)
    photo = models.ImageField(
        blank=True,
        upload_to="uploads/%Y/%m/%d/",
        help_text="Upload a display picture for this person.",
    )
    background = models.TextField(
        blank=True,
        help_text="Provide a short backgound information.",
    )
    is_celebrity = models.BooleanField(
        default=False,
        help_text="Is this person is a celebrity?",
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name_plural = "people"


class BrandKeyPerson(models.Model):
    class Designation(models.TextChoices):
        FOUNDER = "FR"
        CO_FOUNDER = "CFR"
        DIRECTOR = "DR"
        VICE_PRESIDENT = "VP"

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True)
    designation = models.CharField(max_length=4, choices=Designation.choices)

    def __str__(self):
        return f"[{self.brand.name}] [{self.designation}] {self.person.name}"

    class Meta:
        verbose_name_plural = "key people"


class BrandEndorsement(models.Model):
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, help_text="Select a brand."
    )
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        help_text="Select from existing people.",
    )
    collection_name = models.CharField(
        max_length=50,
        help_text="Provide the product collection name.",
    )

    def __str__(self):
        return (
            f"[{self.brand.name}] [{self.person.name}] {self.collection_name}"
        )


class BrandBestseller(models.Model):
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, help_text="Select a brand."
    )
    collection_name = models.CharField(
        max_length=50,
        help_text="Provide the product collection name.",
    )
    collection_date = models.CharField(
        max_length=50,
        help_text="Provide month and year. Ex: May 2023",
    )

    def __str__(self):
        return f"[{self.brand.name}] {self.collection_name}"


class BrandAsset(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)

    asset = models.FileField(
        upload_to="uploads/%Y/%m/%d/",
        help_text="Select an image that you want to upload.",
    )
    title = models.CharField(
        max_length=100,
        help_text="Provide a title for this image.",
    )

    endorsement = models.ForeignKey(
        BrandEndorsement,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Associate with an endorsement, if applicable.",
    )
    bestseller = models.ForeignKey(
        BrandBestseller,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Associate with a bestseller, if applicable.",
    )
    sequence = models.PositiveIntegerField(default=1)

    uploaded_at = models.DateTimeField(default=current_india_time)

    def get_absolute_url(self):
        return self.asset.url

    def __str__(self):
        return f"[{self.brand.name}] {self.title}"


class BrandVisual(models.Model):
    brand = models.OneToOneField(
        Brand, on_delete=models.CASCADE, help_text="Select a brand."
    )

    logo = models.ForeignKey(
        BrandAsset,
        on_delete=models.SET_NULL,
        related_name="brand_logo",
        blank=True,
        null=True,
        help_text="Select from existing image assets.",
    )
    cover = models.ForeignKey(
        BrandAsset,
        on_delete=models.SET_NULL,
        related_name="brand_cover",
        blank=True,
        null=True,
        help_text="Select from existing image assets.",
    )

    def __str__(self):
        return f"Visuals for {self.brand.name}"


class Category(models.Model):
    internal_name = LowerCaseCharField(max_length=15)
    display_name = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.display_name}"

    class Meta:
        verbose_name_plural = "categories"
        constraints = [
            UniqueConstraint(
                Lower("internal_name"),
                name="unique_case_insensitive_category_internal_name",
            ),
            UniqueConstraint(
                Lower("display_name"),
                name="unique_case_insensitive_category_display_name",
            ),
        ]


class Tag(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    name = LowerCaseCharField(max_length=30)
    value = LowerCaseCharField(max_length=50)
    sequence = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"[{self.category}] {self.name}={self.value}"

    class Meta:
        constraints = [
            UniqueConstraint(
                "category",
                "name",
                "value",
                name="unique_tag_name_value_pair_per_category",
            )
        ]


class BrandCategory(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    keywords = models.TextField(blank=True)

    def __str__(self):
        return f"[{self.brand.name}] {self.category.display_name}"

    class Meta:
        verbose_name_plural = "brand categories"
        constraints = [
            UniqueConstraint(
                "brand", "category", name="unique_brand_category_pair"
            )
        ]


class BrandTag(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.PROTECT)

    @property
    def brand_category_exists(self):
        return BrandCategory.objects.filter(
            brand=self.brand, category=self.tag.category
        ).exists()

    def clean(self):
        if not self.brand_category_exists:
            raise ValidationError(
                f"{self.brand} doesn't belong to category {self.tag.category}."
            )

    def __str__(self):
        return f"[{self.brand}] {self.tag}"

    class Meta:
        constraints = [
            UniqueConstraint(
                "brand", "tag", name="unique_brand_tag_per_category"
            )
        ]
