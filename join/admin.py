from django.contrib import admin
from join.models import CollectionPoint, BagType, Customer, OrderChange, BagQuantity, CollectionPointChange, AccountStatusChange


class AccountStatusChangeAdmin(admin.ModelAdmin):
    pass


class CollectionPointAdmin(admin.ModelAdmin):
    pass


class BagTypeAdmin(admin.ModelAdmin):
    pass


class CustomerAdmin(admin.ModelAdmin):
    pass


class OrderChangeAdmin(admin.ModelAdmin):
    pass


class CollectionPointChangeAdmin(admin.ModelAdmin):
    pass


class BagQuantityAdmin(admin.ModelAdmin):
    pass


admin.site.register(AccountStatusChange, AccountStatusChangeAdmin)
admin.site.register(CollectionPoint, CollectionPointAdmin)
admin.site.register(BagType, BagTypeAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(CollectionPointChange, CollectionPointChangeAdmin)
admin.site.register(OrderChange, OrderChangeAdmin)
admin.site.register(BagQuantity, BagQuantityAdmin)
