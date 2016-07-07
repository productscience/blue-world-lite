from decimal import Decimal
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.core import urlresolvers
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from hijack import settings as hijack_settings
from join.helper import get_current_request
from join.models import (
    AccountStatusChange,
    BagType,
    BagTypeCostChange,
    CollectionPoint,
    Customer,
    CustomerCollectionPointChange,
    CustomerOrderChange,
    CustomerOrderChangeBagQuantity,
    CustomerTag,
)


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


class UserAdmin(BaseUserAdmin):
    pass


class BagTypeForm(forms.ModelForm):

    weekly_cost = forms.DecimalField(
        required=True,
        min_value=0,
        max_value=500,
        max_digits=6,
        decimal_places=2,
    )

    def __init__(self, *k, **p):
        if p.get('instance'):
            # Edit case
            initial = p.get('iniital', {})
            initial['weekly_cost'] = p['instance'].weekly_cost
            p['initial'] = initial
        super(BagTypeForm, self).__init__(*k, **p)

    def save(self, commit=True):
        weekly_cost = Decimal(self.cleaned_data.get('weekly_cost', None))
        bag_type = super(BagTypeForm, self).save(commit=commit)
        bag_type.save()
        bag_type.weekly_cost = weekly_cost
        return bag_type

    class Meta:
        model = BagType
        fields = '__all__'


class BagTypeAdmin(BlueWorldModelAdmin):
    form = BagTypeForm
    # fields = ('name', 'display_order', 'active', 'weekly_cost')
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'display_order',
                'active',
                'weekly_cost',
                'cost_changes',
            ),
        }),
    )
    list_display = ('name', 'active', 'weekly_cost')

    def cost_changes(self, obj):
        # XXX Not tested yet
        result = ''
        cost_changes = obj.cost_changes.order_by('-changed').all()
        for i, cost_change in enumerate(cost_changes):
            if i == len(cost_changes) - 1:
                result += '<b>£{}</b> - inital value set at {}<br>'.format(
                    cost_change.weekly_cost,
                    cost_change.changed.strftime('%Y-%m-%d %H:%M'),
                )
            else:
                result += '<b>£{}</b> - changed at {}<br>'.format(
                    cost_change.weekly_cost,
                    cost_change.changed.strftime('%Y-%m-%d %H:%M'),
                )
        return mark_safe(result)
    cost_changes.short_description = 'Cost Changes'

    def get_readonly_fields(self, request, obj=None):
        return ['cost_changes']

    # def has_add_permission(self, request, obj=None):
    #     return False

    # def formfield_for_dbfield(self, db_field, **kwargs):
    #     field = super(BagTypeAdmin, self).formfield_for_dbfield(
    #         db_field, **kwargs)
    #     import pdb; pdb.set_trace()
    #     return field


class AccountStatusListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('account status')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'latest_account_status'

    def lookups(self, request, model_admin):
        return AccountStatusChange.STATUS_CHOICES

    def queryset(self, request, queryset):
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() is None:
            return queryset
        customer_ids = []
        for customer in queryset.filter(
            account_status_change__status=self.value()
        ).all():
            if customer.account_status == self.value():
                customer_ids.append(customer.pk)
        return queryset.filter(pk__in=customer_ids)


class CollectionPointFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('collection point')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'collection_point'

    def lookups(self, request, model_admin):
        return [(cp.id, cp.name) for cp in CollectionPoint.objects.all()]

    def queryset(self, request, queryset):
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() is None:
            return queryset
        customer_ids = []
        for customer in queryset.all():
            if customer.collection_point.id == int(self.value()):
                customer_ids.append(customer.id)
        return queryset.filter(pk__in=customer_ids)


class CustomerAdmin(BlueWorldModelAdmin):
    search_fields = ('full_name', 'nickname', )
    list_display = (
        'full_name',
        'account_status',  # Dynamically generated latest value
        'tags_field',
        'bag_quantities',
        'collection_point',  # Dynamically generated latest value
        'hijack_field',  # Hijack button
    )
    list_filter = (
        AccountStatusListFilter,
        'tags__tag',
        CollectionPointFilter,
    )

    def hijack_field(self, obj):
        hijack_attributes = hijack_settings.HIJACK_URL_ALLOWED_ATTRIBUTES
        assert 'user_id' in hijack_attributes
        hijack_url = reverse('login_with_id', args=(obj.user.pk, ))
        button_template = get_template(settings.HIJACK_BUTTON_TEMPLATE)
        button_context = RequestContext(get_current_request(), {
            'request': get_current_request(),
            'user_id': obj.user.pk,
            'hijack_url': hijack_url,
            'username': str(obj),
            'full_name': obj.full_name,
        })
        return button_template.render(button_context)

    hijack_field.allow_tags = True
    hijack_field.short_description = _('Become user')

    # readonly_fields = ['user_link']
    # def user_link(self, obj):
    #     change_url = urlresolvers.reverse(
    #         'admin:auth_user_change',
    #         args=(obj.user.id,)
    #     )
    #     return mark_safe('<a href="%s">%s</a>' % (
    #         change_url, obj.user.email))
    # user_link.short_description = 'User'

    def bag_quantities(self, obj):
        result = ''
        for bag_quantity in obj.bag_quantities:
            result += '{} x {}\n'.format(
                bag_quantity.quantity,
                bag_quantity.bag_type.name,
            )
        return result
    bag_quantities.short_description = 'Bag quantities'

    def tags_field(self, obj):
        result = ''
        for tag in obj.tags.all():
            result += '{}\n'.format(tag.tag)
        return result
    tags_field.short_description = 'Tags'

    def get_readonly_fields(self, request, obj=None):
        return [
            'user',
            'full_name',
            'nickname',
            'mobile',
            'go_cardless',
            'collection_point',
            'bag_quantities',
        ]
        # result = list(self.readonly_fields) + \
        #        [field.name for field in obj._meta.fields] + \
        #        [ 'collection_point', 'bag_quantities']
        # return result

    def has_add_permission(self, request, obj=None):
        return False

    fields = [
        'user',
        'full_name',
        'nickname',
        'mobile',
        'go_cardless',
        'collection_point',
        'bag_quantities',
        'tags',
    ]


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
admin.site.register(
    CustomerCollectionPointChange,
    CustomerCollectionPointChangeAdmin,
)
admin.site.register(CustomerOrderChange, CustomerOrderChangeAdmin)
admin.site.register(
    CustomerOrderChangeBagQuantity,
    CustomerOrderChangeBagQuantityAdmin,
)
admin.site.register(CustomerTag, CustomerTagAdmin)
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)
admin.site.disable_action('delete_selected')
