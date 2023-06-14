from django.contrib import admin
from django.db.models.functions import Lower

from brand.models import (
    Brand,
    BrandAsset,
    BrandBestseller,
    BrandCategory,
    BrandEndorsement,
    BrandKeyPerson,
    BrandOnlineStore,
    BrandTag,
    BrandVisual,
    Category,
    OnlineStore,
    Person,
    Tag,
)


class BrandAdmin(admin.ModelAdmin):
    exclude = (
        "user_rating",
        "brandscanner_rating",
        "page_views",
        "last_updated",
    )


class AssetAdmin(admin.ModelAdmin):
    exclude = ("uploaded_at",)


class TagAdmin(admin.ModelAdmin):
    ordering = [Lower("name"), Lower("value")]


admin.site.register(Brand, BrandAdmin)
admin.site.register(BrandAsset, AssetAdmin)
admin.site.register(BrandVisual)
admin.site.register(Person)
admin.site.register(BrandKeyPerson)
admin.site.register(BrandEndorsement)
admin.site.register(BrandBestseller)
admin.site.register(OnlineStore)
admin.site.register(BrandOnlineStore)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(BrandCategory)
admin.site.register(BrandTag)
