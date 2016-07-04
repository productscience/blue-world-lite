from django.contrib import admin
from django.utils.safestring import mark_safe
from django.core import urlresolvers
from join.models import CollectionPoint, BagType, Customer, CustomerOrderChange, CustomerOrderChangeBagQuantity, CustomerCollectionPointChange, AccountStatusChange

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from hijack_admin.admin import HijackUserAdminMixin



from django.core.urlresolvers import reverse
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _
from django import VERSION

from hijack import settings as hijack_settings
from hijack_admin import settings as hijack_admin_settings

if VERSION < (1, 8):
    from django.template import Context


class BlueWorldModelAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


class AccountStatusChangeAdmin(BlueWorldModelAdmin):
    pass


class CollectionPointAdmin(BlueWorldModelAdmin):
    list_display = (
        'name',
        'active',
        'display_order',
    )


class UserAdmin(BaseUserAdmin, HijackUserAdminMixin):
    pass
#     list_display = (
#         'username',
#         # 'hijack_field',  # Hijack button
#     )
# 
# UserAdmin.fieldsets[0][1]['fields'] = tuple(list(UserAdmin.fieldsets[0][1]['fields']) + ['hijack_field'])


class BagTypeAdmin(BlueWorldModelAdmin):
    pass


class CustomerAdmin(BlueWorldModelAdmin):
    # ['user_link', 'id', 'user', 'full_name', 'nickname', 'mobile', 'go_cardless']
    search_fields = ('full_name', 'nickname', )
    list_display = (
        'full_name',
        'user_link',
        'nickname',
        'hijack_field',  # Hijack button
    )

    def hijack_field(self, obj):
        hijack_attributes = hijack_settings.HIJACK_URL_ALLOWED_ATTRIBUTES

        assert 'user_id' in hijack_attributes
        hijack_url = reverse('login_with_id', args=(obj.user.pk, ))

        button_template = get_template(hijack_admin_settings.HIJACK_BUTTON_TEMPLATE)
        button_context = {
            'hijack_url': hijack_url,
            'username': str(obj),
        }
        if VERSION < (1, 8):
            button_context = Context(button_context)

        return button_template.render(button_context)

    hijack_field.allow_tags = True
    hijack_field.short_description = _('Become user')


    readonly_fields = ['user_link']

    def user_link(self, obj):
        change_url = urlresolvers.reverse('admin:auth_user_change', args=(obj.user.id,))
        return mark_safe('<a href="%s">%s</a>' % (change_url, obj.user.email))
    user_link.short_description = 'User'

    def get_readonly_fields(self, request, obj=None):
        result = list(self.readonly_fields) + \
               [field.name for field in obj._meta.fields]
        return result

    def has_add_permission(self, request, obj=None):
        return False



class CustomerOrderChangeAdmin(BlueWorldModelAdmin):
    pass


class CustomerCollectionPointChangeAdmin(BlueWorldModelAdmin):
    pass


class CustomerOrderChangeBagQuantityAdmin(BlueWorldModelAdmin):
    pass


admin.site.register(AccountStatusChange, AccountStatusChangeAdmin)
admin.site.register(CollectionPoint, CollectionPointAdmin)
admin.site.register(BagType, BagTypeAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomerCollectionPointChange, CustomerCollectionPointChangeAdmin)
admin.site.register(CustomerOrderChange, CustomerOrderChangeAdmin)
admin.site.register(CustomerOrderChangeBagQuantity, CustomerOrderChangeBagQuantityAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.disable_action('delete_selected')
