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
            raise ValidationError('Not a valid billing week. Error was: {}'.format(e))


class PackingListForm(forms.Form):
    billing_week = BillingWeekField(
        max_length=9,
        strip=True,
        help_text='Based on these <a href="{}">billing dates</a>. e.g. <tt>2016-07 4</tt>'.format(
            '/billing-dates' # XXX Not working: reverse('blueworld:billing_dates')
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
        initial = {'billing_week': str(get_billing_week(now))}
        if '_generate' in request.POST:
            form = PackingListForm(request.POST, initial=initial)
            if form.is_valid():
                return generate_packing_list(
                    self,
                    request,
                    queryset,
                    parse_billing_week(form.cleaned_data['billing_week']),
                )
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
        ascs = AccountStatusChange.objects.order_by(
            'customer', '-changed'
        ).distinct('customer').only('id')
        customer_ids = [c.customer_id for c in ascs if c.status == self.value()]
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
        customer_ids = [c.customer_id for c in ccpcs if c.collection_point.pk == int(self.value())]
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

    fields = [
        'user',
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


def generate_packing_list(model_admin, request, queryset, pl_bw):
    #import pdb; pdb.set_trace()
    # Can't use filter() with distinct() because Django applies the filter() first
    # so instead we do all the joins manually in memory
    # collection_date = (deadline_date + timedelta(3)).replace(hour=0)

    # deadline_day = collection_date - timedelta(3)
    # deadline_date = deadline_day.replace(
    #     hour=15,
    #     minute=0,
    #     second=0,
    #     microsecond=0,
    # )
    # print(deadline_date.isoformat())

    #assert deadline_date.weekday() == 6 and deadline_date.hour == 15 and deadline_date.minute == 0 and deadline_date.second == 0 and deadline_date.microsecond == 0 and deadline_date.tzinfo == timezone.get_default_timezone(), 'Not a valid deadline date: {}'.format(deadline_date)
    now = timezone.now()
    bw = get_billing_week(now)
    #print(now, collection_date, deadline_date)
    bag_types = []
    bag_type_tag_color = {}
    for bag_type in BagType.objects.order_by('name').distinct('name'):
        bag_types.append(bag_type.name)
        bag_type_tag_color[bag_type.name] = bag_type.tag_color
    collection_point_ids = [collection_point.id for collection_point in queryset]
    collection_point_days = dict([(collection_point.name, collection_point.get_collection_day_display()) for collection_point in queryset])
    ccpcs = CustomerCollectionPointChange.objects.filter(changed_in_billing_week__lt=pl_bw.start).order_by(
        'customer', '-changed'
    ).distinct('customer').only('customer_id', 'collection_point_id')
    customer_ids = [ccpc.customer_id for ccpc in ccpcs if ccpc.collection_point_id in collection_point_ids]
    starters = Customer.objects.filter(pk__in=customer_ids, tags__in=CustomerTag.objects.filter(tag='Starter')).values_list('full_name', flat=True)
    order_changes = CustomerOrderChange.objects.order_by(
        'customer', '-changed'
    ).distinct('customer').only('customer_id', 'id')
    order_change_ids = [order_change.id for order_change in order_changes if order_change.customer_id in customer_ids]
    bqs = CustomerOrderChangeBagQuantity.objects.filter(
        customer_order_change__in=order_change_ids
    ).order_by('customer_order_change__customer__full_name').only('customer_order_change__customer')
    # print(Skip.objects.filter(
    #     customer_id__in=customer_ids,
    #     collection_date=collection_date,
    # ).query.__str__())
    # import pdb; pdb.set_trace()
    skips = Skip.objects.filter(
        customer_id__in=customer_ids,
        billing_week=str(pl_bw),
        #collection_date=collection_date,
    ).values_list('customer__full_name', flat=True)
    #print(customer_ids, skips)
    cps = OrderedDict()
    cp_counts = OrderedDict()
    cp_holiday_counts = OrderedDict()
    cp_user_counts = OrderedDict()
    cp_total_by_bags = OrderedDict()
    cp_total_by_collection_point = OrderedDict()
    for bag_type in bag_types:
        cp_total_by_bags[bag_type] = 0
    for bq in bqs:
        collection_point = bq.customer_order_change.customer.collection_point
        if collection_point.name not in cps:
            cps[collection_point.name] = OrderedDict()
            cp_counts[collection_point.name] = OrderedDict()
            cp_holiday_counts[collection_point.name] = []
            cp_user_counts[collection_point.name] = []
            cp_total_by_collection_point[collection_point.name] = 0
            for bag_type in bag_types:
                cp_counts[collection_point.name][bag_type] = 0
        if bq.customer_order_change.customer.full_name not in cps[collection_point.name]:
            cps[collection_point.name][bq.customer_order_change.customer.full_name] = {
                bq.bag_type.name: bq.quantity
            }
        else:
            assert bq.bag_type.name not in cps[collection_point.name][bq.customer_order_change.customer.full_name]
            cps[collection_point.name][
                bq.customer_order_change.customer.full_name
            ][bq.bag_type.name] = bq.quantity
        if bq.customer_order_change.customer.full_name not in skips:
            cp_counts[collection_point.name][bq.bag_type.name] += bq.quantity
            cp_total_by_bags[bq.bag_type.name] += bq.quantity
            cp_total_by_collection_point[collection_point.name] += bq.quantity
            if bq.customer_order_change.customer.full_name not in cp_user_counts[collection_point.name]:
                # Want unique customers here, if the customer has more than one
                # bag we could double count if we just added 1 each time.
                cp_user_counts[collection_point.name].append(bq.customer_order_change.customer.full_name)
        elif bq.customer_order_change.customer.full_name not in cp_holiday_counts[collection_point.name]:
            # Want unique customers here, if the customer has more than one
            # bag we could double count if we just added 1 each time.
            cp_holiday_counts[collection_point.name].append(bq.customer_order_change.customer.full_name)
    # rows_updated = len(cps)
    # if rows_updated == 1:
    #     message_bit = '''
    #         packing list generated successfully for 1 collection point
    #     '''
    # else:
    #     message_bit = '''
    #         packing lists generated successfully for %s collection points
    #     ''' % rows_updated
    # model_admin.message_user(request, "%s." % message_bit)
    assert sum(cp_total_by_bags.values()) == sum(cp_total_by_collection_point.values())
    return render(
        request,
        'packing-list.html',
        {
            'collection_points': cps,
            'collection_point_counts': cp_counts,
            'collection_point_holiday_counts': cp_holiday_counts,
            'collection_point_user_counts': cp_user_counts,
            'total_by_bags': cp_total_by_bags,
            'total_by_collection_point': cp_total_by_collection_point,
            'total_holidays': sum([len(v) for v in cp_holiday_counts.values()]),
            'total_users': sum([len(v) for v in cp_user_counts.values()]),
            'total_bags': sum(cp_total_by_bags.values()),
            'collection_point_days': collection_point_days,
            'bag_types': bag_types,
            'bag_type_tag_color': bag_type_tag_color,
            'skips': skips,
            'now': now,
            'now_bw': bw,
            'pl_bw': pl_bw,
            'starters': starters,
        },
    )
