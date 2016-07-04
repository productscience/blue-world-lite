from django.contrib import admin
from django.utils.safestring import mark_safe
from django.core import urlresolvers
from join.models import CollectionPoint, BagType, Customer, CustomerOrderChange, CustomerOrderChangeBagQuantity, CustomerCollectionPointChange, AccountStatusChange, CustomerTag

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





from datetime import date

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class AccountStatusListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('account status')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'latest_account_status'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return AccountStatusChange.STATUS_CHOICES

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() is None:
            return queryset
        customer_ids = [customer.pk for customer in queryset.filter(account_status_change__status=self.value()).all() if customer.account_status==self.value()]
        return queryset.filter(pk__in=customer_ids)


class CustomerAdmin(BlueWorldModelAdmin):
    # ['user_link', 'id', 'user', 'full_name', 'nickname', 'mobile', 'go_cardless']
    search_fields = ('full_name', 'nickname', )
    list_display = (
        'full_name',
     #   'user_link',
        #'nickname',
        'hijack_field',  # Hijack button
        'account_status', # Dynamically generated latest value
        'tags_field',
        # 'collection_point', # Dynamically generated latest value
        # 'bag_quantities',
    )
    list_filter = (
        AccountStatusListFilter,
        'tags__tag',
    )
    # list_filter = ('account_status_change__status', admin.RelatedOnlyFieldListFilter),

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

    # readonly_fields = ['user_link']

    # def user_link(self, obj):
    #     change_url = urlresolvers.reverse('admin:auth_user_change', args=(obj.user.id,))
    #     return mark_safe('<a href="%s">%s</a>' % (change_url, obj.user.email))
    # user_link.short_description = 'User'

    def bag_quantities(self, obj):
        result = ''
        for bag_quantity in obj.bag_quantities.all():
            result += '{} x {}\n'.format(bag_quantity.quantity, bag_quantity.bag_type.name)
        return result
    bag_quantities.short_description = 'Bag quantities'

    def tags_field(self, obj):
        result = ''
        for tag in obj.tags.all():
            result += '{}\n'.format(tag.tag)
        return result
    #     return mark_safe('<a href="%s">%s</a>' % (change_url, obj.user.email))
    tags_field.short_description = 'Bag quantities'

    def get_readonly_fields(self, request, obj=None):
        return ['user', 'full_name', 'nickname', 'mobile', 'go_cardless','collection_point', 'bag_quantities']
        result = list(self.readonly_fields) + \
               [field.name for field in obj._meta.fields] + \
               [ 'collection_point', 'bag_quantities']
        return result

    def has_add_permission(self, request, obj=None):
        return False

    fields = ['user', 'full_name', 'nickname', 'mobile', 'go_cardless','collection_point', 'bag_quantities', 'tags']

class CustomerOrderChangeAdmin(BlueWorldModelAdmin):
    pass


class CustomerCollectionPointChangeAdmin(BlueWorldModelAdmin):
    pass


class CustomerOrderChangeBagQuantityAdmin(BlueWorldModelAdmin):
    pass


class CustomerTagAdmin(BlueWorldModelAdmin):
    pass


admin.site.register(AccountStatusChange, AccountStatusChangeAdmin)
admin.site.register(CollectionPoint, CollectionPointAdmin)
admin.site.register(BagType, BagTypeAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomerCollectionPointChange, CustomerCollectionPointChangeAdmin)
admin.site.register(CustomerOrderChange, CustomerOrderChangeAdmin)
admin.site.register(CustomerOrderChangeBagQuantity, CustomerOrderChangeBagQuantityAdmin)
admin.site.register(CustomerTag, CustomerTagAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.disable_action('delete_selected')
