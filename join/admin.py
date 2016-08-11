from collections import OrderedDict
from datetime import timedelta
from decimal import Decimal
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.core import urlresolvers
from django.core.urlresolvers import reverse
from django.db import connection
from django.db import reset_queries
from django.shortcuts import render
from django.template import RequestContext
from django.template.loader import get_template
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from hijack import settings as hijack_settings
from join.helper import get_current_request, render_bag_quantities
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
    Reminder,
    Skip,
)
from django.contrib.admin import widgets as admin_widgets
from django.core.exceptions import ValidationError
from billing_week import get_billing_week, parse_billing_week


class BlueWorldModelAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


class AccountStatusChangeAdmin(BlueWorldModelAdmin):
    pass


class BillingWeekField(forms.CharField):
    def validate(self, value):
        # Use the parent's handling of required fields, etc.
        super().validate(value)
        try:
            return parse_billing_week(value)
        except Exception as e:
            raise ValidationError(
                'Not a valid billing week. Error was: {}'.format(e)
            )


class PackingListForm(forms.Form):
    billing_week = BillingWeekField(
        max_length=9,
        strip=True,
        help_text=(
            'Based on these <a href="{}">billing dates</a>. '
            'e.g. <tt>2016-07 4</tt>'
        ).format(
            # XXX Not working: reverse('blueworld:billing_dates')
            '/billing-dates'
        ),
    )


class CollectionPointAdmin(BlueWorldModelAdmin):
    actions = ['packing_list']
    list_display = (
        'name',
        'active',
        'display_order',
    )

    def packing_list(self, request, queryset):
        now = timezone.now()
        bw = get_billing_week(now)
        initial = {
            'billing_week': str(bw)
        }
        if '_generate' in request.POST:
            form = PackingListForm(request.POST, initial=initial)
            if form.is_valid():
                context = packing_list(
                    queryset,
                    parse_billing_week(form.cleaned_data['billing_week'])
                )
                context['now_billing_week'] = bw
                # context['now_billing_week'] = context['billing_week']
                context['now'] = now
                return render(request, 'packing-list.html', context)
        else:
            form = PackingListForm(initial=initial)
        return render(
            request,
            'packing-list-date.html',
            {
                'form': form,
                'post_vars': request.POST.lists(),

                'opts': CollectionPoint._meta,
                'change': True,
                'is_popup': False,
                'save_as': False,
                'has_delete_permission': False,
                'has_add_permission': False,
                'has_change_permission': False,
            }
        )

    packing_list.short_description = \
        "Generated packing list for selected collection points"


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
                'tag_color',
            ),
        }),
    )
    list_display = ('name', 'tag_color', 'active', 'weekly_cost')

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
        ascs = AccountStatusChange.objects.order_by(
            'customer', '-changed'
        ).distinct('customer').only('id')
        customer_ids = [
            c.customer_id for c in ascs if c.status == self.value()
        ]
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
        if self.value() is None:
            return queryset
        # Note: You can't use a filter here
        ccpcs = CustomerCollectionPointChange.objects.order_by(
            'customer', '-changed'
        ).distinct('customer').only('id')
        customer_ids = [
            c.customer_id for c in ccpcs
            if c.collection_point.pk == int(self.value())
        ]
        return queryset.filter(pk__in=customer_ids)

class ReminderDueListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter optiion
    title = "Reminders"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'reminders'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return [
            ('due', _('Only with reminders'))
        ]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.

        if self.value() == 'due':
            return queryset.filter(reminder__done=False)

class ReminderInline(admin.StackedInline):
    model = Reminder
    extra = 0
    template = "admin/join/customer/stacked_inline.html"


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
        ReminderDueListFilter,
    )

    inlines = [ReminderInline]

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
        return render_bag_quantities(obj.bag_quantities.all())
    bag_quantities.short_description = 'Bag quantities'

    def tags_field(self, obj):
        result = ''
        for tag in obj.tags.all():
            result += '{}\n'.format(tag.tag)
        return result
    tags_field.short_description = 'Tags'

    def current_mandate(self, obj):
        return obj.gocardless_current_mandate.gocardless_mandate_id
    current_mandate.short_description = 'Gocardless current mandate'

    def get_readonly_fields(self, request, obj=None):
        return [
            'user',
            'account_status',
            'current_mandate',
            'collection_point',
            'bag_quantities',
        ]
        # result = list(self.readonly_fields) + \
        #        [field.name for field in obj._meta.fields] + \
        #        [ 'collection_point', 'bag_quantities']
        # return result

    def has_add_permission(self, request, obj=None):
        return False

    # controls which fields to display in the change form
    fields = [
        'account_status',
        'full_name',
        'nickname',
        'mobile',
        'current_mandate',
        'collection_point',
        'bag_quantities',
        'holiday_due',
        'balance_carried_over',
        'tags',
    ]

    def change_view(self, request, object_id, extra_context=None):
        """
        Overrides the normal change form view to lets us add vars, for linking
        to external services, like Helpscout.
        """
        obj = Customer.objects.get(pk=object_id)

        my_context = {
            'name_for_helpscout': obj.full_name,
            'customer_user': obj.user.id
        }
        return super(CustomerAdmin, self).change_view(request, object_id,
            extra_context=my_context)


class CustomerOrderChangeAdmin(BlueWorldModelAdmin):
    pass


class CustomerCollectionPointChangeAdmin(BlueWorldModelAdmin):
    pass


class CustomerOrderChangeBagQuantityAdmin(BlueWorldModelAdmin):
    pass


class CustomerTagAdmin(BlueWorldModelAdmin):
    pass


class SkipAdmin(BlueWorldModelAdmin):
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
admin.site.register(Skip, SkipAdmin)
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)
admin.site.disable_action('delete_selected')


def packing_list(collection_points, billing_week):
    '''
    We'll need the following data strucutures:

    `bag_name`:                         A lookup of bag ID to bag name
    `collection_point_name`:            A lookup of bag ID to bag name
    `customer_name`:                    A lookup of customer ID to customer
                                        name
    `customer_latest_bag_quantities`
    `customer_latest_collection_point`

    Although it would be faster to do all this in the database, in terms of
    scalability, assembling everything in Django from separate data means
    the database does less work, and that the database could be partitioned
    in future.

    Although it would be easier to start with just the collection points
    and then just use model attributes to assemble everything else, that
    would be a lot slower (as it would create thousands of queries)

    Although it would be neater to use custom querysets and model hacks
    to make all this look seamless, that would be more complex and less
    maintainable in the long term.

    So we create a "reporting model" which is a tree a bit like a model
    but where each stage of the hierarchy is keyed by an ID, and which
    only has the properties we've already fetched from the database.

    Then we'll put it all together into a big packing_list that looks like
    this:

        collection_point = packing_list[collection_point_id]
        collection_point.name
        collection_point.collection_day

        collection_point.total.bags.all
        collection_point.total.bags.by_id[bag_id]
        collection_point.total.customers.all
        collection_point.total.customers.on_holiday
        collection_point.total.customers.collecting

        customer = collection_point.current_customer[customer_id]
        customer.bags[bag_id] = bag_quantity
        customer.new          = True/False
        customer.holiday      = True/False

    Note that although we can go backwards in time on holiday status,
    collection points and orders, the names, collection_day and Starter status
    are only valid until the last deadline.
    '''
    bag_types = BagType.objects.all().only('id', 'name', 'tag_color')
    collection_point_name = dict(
        CollectionPoint.objects.all()
        .filter(pk__in=collection_points)
        .only('id', 'name')
        .values_list('id', 'name')
    )
    customer_name = dict(
        Customer.objects.all()
        .only('id', 'full_name')
        .values_list('id', 'full_name')
    )
    _is_on_holiday = (
        Skip.objects
        .filter(billing_week=str(billing_week))
        .only('customer_id')
        .values_list('customer__id', flat=True)
    )
    _is_starter = (
        Customer.objects
        .filter(
            pk__in=customer_name.keys(),
            tags__in=CustomerTag.objects.filter(tag='Starter')
        )
        .only('id')
        .values_list('id', flat=True)
    )
    _latest_bag_quantities = (
        CustomerOrderChangeBagQuantity.objects
        .filter(
            customer_order_change__in=(
                CustomerOrderChange.objects
                .filter(changed_in_billing_week__lt=str(billing_week))
                .order_by('customer', '-changed')
                .distinct('customer')
                .only('id')
            ),
        )
        .order_by('customer_order_change__customer__full_name')
        .only('customer_order_change__customer_id', 'bag_type_id', 'quantity')
    )
    _bags_by_customer = OrderedDict()
    # Must be an OrderedDict to keep everything in the right order
    _no_bags = OrderedDict([(bag_type, 0) for bag_type in bag_types])
    _user_totals = OrderedDict([
        ('collecting', 0),
        ('holiday', 0),
    ])
    for bag_quantity in _latest_bag_quantities:
        customer = bag_quantity.customer_order_change.customer
        if customer not in _bags_by_customer:
            _bags_by_customer[customer] = _no_bags.copy()
        _bags_by_customer[customer][bag_quantity.bag_type] = \
            bag_quantity.quantity
    _latest_collection_points = (
        CustomerCollectionPointChange.objects
        .filter(changed_in_billing_week__lt=str(billing_week))
        .order_by('customer', '-changed')
        .distinct('customer')
        .only(
            'customer_id',
            'collection_point_id',
            'collection_point__collection_day',
        )
    )
    summary_totals = OrderedDict()
    for bag_type in bag_types:
        summary_totals[bag_type] = 0
    for column in ['collecting_users', 'holidaying_users', 'collecting_bags', 'holidaying_bags']:
        summary_totals[column] = 0
    packing_list = OrderedDict()
    bag_totals = OrderedDict()
    for change in _latest_collection_points:
        cp = change.collection_point
        customer = change.customer
        if cp not in packing_list:
            packing_list[cp] = {
                'customers': OrderedDict(),
                'collecting_bag_totals_by_type': _no_bags.copy(),
                'user_totals_by_category': _user_totals.copy(),
                'holiday_bag_total': 0,
                'collecting_bag_total': 0,
            }
        # XXX Outside the tests, all customers should have at least one bag
        _bags = _bags_by_customer.get(customer, _no_bags)
        holiday = customer.id in _is_on_holiday and True or False
        for bag_type, quantity in _bags.items():
            if not holiday:
                packing_list[cp]['collecting_bag_totals_by_type'][bag_type] += quantity
                packing_list[cp]['collecting_bag_total'] += quantity
                summary_totals[bag_type] += quantity
                summary_totals['collecting_bags'] += quantity
            else:
                packing_list[cp]['holiday_bag_total'] += quantity
                summary_totals['holidaying_bags'] += quantity
        packing_list[cp]['customers'][customer] = {
            'bags': _bags,
            'new': customer.id in _is_starter and True or False,
            'holiday': holiday,
        }
        if packing_list[cp]['customers'][customer]['holiday']:
             packing_list[cp]['user_totals_by_category']['holiday'] += 1
             summary_totals['holidaying_users'] += 1
        else:
             packing_list[cp]['user_totals_by_category']['collecting'] += 1
             summary_totals['collecting_users'] += 1
    return {
        'billing_week': billing_week,
        'bag_types': bag_types,
        'packing_list': packing_list,
        'summary_totals': summary_totals,
    }
