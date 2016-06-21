from django.contrib import admin
from join.models import CollectionPoint, BagType


class CollectionPointAdmin(admin.ModelAdmin):
    pass


admin.site.register(CollectionPoint, CollectionPointAdmin)


class BagTypeAdmin(admin.ModelAdmin):
    pass


admin.site.register(BagType, BagTypeAdmin)
