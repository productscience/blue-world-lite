from datetime import timedelta
import datetime
import json
import uuid
from collections import OrderedDict

from billing_week import get_billing_week, parse_billing_week
from allauth.account.views import signup as allauth_signup
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms import BaseFormSet
from django.forms import formset_factory
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.defaulttags import register
from django.utils import formats, timezone
from django.utils.html import format_html, escape
import gocardless_pro

from billing_week import first_wed_of_month as start_of_the_month
from join.helper import get_pickup_dates, render_bag_quantities
from .models import (
    AccountStatusChange,
    BagType,
    BillingGoCardlessMandate,
    Skip,
    CollectionPoint,
    Customer,
    CustomerCollectionPointChange,
    CustomerOrderChange,
    CustomerOrderChangeBagQuantity,
    CustomerTag,
)
import pytz
if settings.TIME_TRAVEL:
    import freezegun


@register.filter
def get_item(dictionary, key):
    assert isinstance(dictionary, dict), "Not a dict: {!r} so can't get {!r}. This can happen if you have specified the variable name of the dictionary incorrectly and it has been replaced with ''.".format(dictionary, key)
    return dictionary.get(key)


# XXX Should this be global?
gocardless_client = gocardless_pro.Client(
    access_token=settings.GOCARDLESS_ACCESS_TOKEN,
    environment=settings.GOCARDLESS_ENVIRONMENT,
)


ERROR_TEMPLATE = '''
<html>
  <h3>{heading}</h3>
  <p>{message}</p>
</html>
'''


FORBIDDEN_TEMPLATE = '''
<html>
  <h1>{heading}</h1>
  <p>{message}</p>
</html>
'''


def not_staff(func):
    def _decorated(request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return HttpResponseForbidden(
                FORBIDDEN_TEMPLATE.format(
                    heading='Staff don\'t have a dashboard',
                    message=''
                )
            )
        return func(request, *args, **kwargs)
    return _decorated


def gocardless_is_set_up(func):
    def _decorated(request, *args, **kwargs):
        if not request.user.customer.gocardless_current_mandate:
            return redirect(reverse('dashboard_gocardless'))
        return func(request, *args, **kwargs)
    return _decorated


def gocardless_is_not_set_up(func):
    def _decorated(request, *args, **kwargs):
        if request.user.customer.gocardless_current_mandate:
            return HttpResponseForbidden(
                FORBIDDEN_TEMPLATE.format(
                    heading='Go Cardless is Already Set Up',
                    message=''
                )
            )
        return func(request, *args, **kwargs)
    return _decorated


def have_not_left_scheme(func):
    def _decorated(request, *args, **kwargs):
        if request.user.customer.account_status == AccountStatusChange.LEFT:
            return HttpResponseForbidden(
                FORBIDDEN_TEMPLATE.format(
                    heading='You have left the scheme',
                    message='',
                )
            )
        return func(request, *args, **kwargs)
    return _decorated


def have_left_scheme(func):
    def _decorated(request, *args, **kwargs):
        if request.user.customer.account_status != AccountStatusChange.LEFT:
            return redirect(reverse('dashboard'))
        return func(request, *args, **kwargs)
    return _decorated


class QuantityForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(
        min_value=0,
        max_value=100,
        # Don't want to use an HTML5 number field in case old browsers
        # don't cope
        widget=forms.widgets.TextInput()
    )


class BaseOrderFormSet(BaseFormSet):
    def clean(self):
        """Checks that at least one bag has been ordered"""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid
            # on its own
            return
        total_bags = 0
        last_bag = None
        for form in self.forms:
            total_bags += form.cleaned_data['quantity']
            if form.cleaned_data['quantity']:
                last_bag = form.initial['name']
        # Do we want to validate this?
        if total_bags < 1:
            raise forms.ValidationError(
                "Please choose at least one bag to order."
            )
        if total_bags == 1 and last_bag == settings.SMALL_FRUIT_BAG_NAME:
            raise forms.ValidationError(
                "You must choose another bag too if you order "
                "small fruit"
            )


class CollectionPointModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if obj.location:
            return format_html("{} <small>{}</small>", obj.name, obj.location)
        else:
            return format_html("{}", obj.name)


class CollectionPointForm(forms.Form):
    collection_point = CollectionPointModelChoiceField(
        queryset=CollectionPoint.objects.order_by(
            'display_order'
        ).filter(active=True),
        widget=forms.RadioSelect(),
        empty_label=None,
    )


class SkipForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    skipped = forms.BooleanField(required=False)


class BaseSkipFormSet(BaseFormSet):
    def clean(self):
        """Checks that no dates are before the last skip date"""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid
            # on its own
            return
        if not len(self.initial) == len(self.cleaned_data):
            raise forms.ValidationError(
                "Some of the data you had entered is no longer valid. "
                "Please review your choices and try again."
            )
        for i, initial in enumerate(self.initial):
            if self.cleaned_data[i]['id'] != self.initial[i]['id']:
                raise forms.ValidationError(
                    "Some of the data you had entered is no longer valid. "
                    "Please review your choices and try again."
                )


@login_required
@not_staff
@gocardless_is_set_up
def dashboard_skip_weeks(request):
    now = timezone.now()
    bw = get_billing_week(now)
    if request.method == 'POST' and request.POST.get('cancel'):
        messages.add_message(
            request,
            messages.INFO,
            'Your skip weeks have not been changed.'
        )
        return redirect(reverse("dashboard"))

    SkipFormSet = formset_factory(
        SkipForm,
        extra=0,
        formset=BaseSkipFormSet,
    )

    # We want to see the next 9 skip weeks we can change
    # We can't change things in the current billing week but
    # but we can change things in the next billing week
    skipped_billing_weeks = []
    if settings.ALLOW_SKIP_CURRENT_WEEK:
        startbw = bw
        bwqstr = str(bw)
    else:
        startbw = bw.next()
        bwqstr = str(startbw)
    for skip in Skip.objects.order_by(
            'billing_week'
       ).filter(
           customer=request.user.customer,
           billing_week__gte=bwqstr,
       ):
        skipped_billing_weeks.append(skip.billing_week)

    valid_dates = {}
    initial_skips = []
    # Offer dates this month and for the next two.
    for month, pickup_dates in get_pickup_dates(startbw.wed, 9).items():
        for skipbw in pickup_dates:
            pickup_date = skipbw.wed
            skip_choice = {
                'id': str(skipbw),
                'skipbw': skipbw,
                'skipped': str(skipbw) in skipped_billing_weeks,
            }
            initial_skips.append(skip_choice)
            valid_dates[str(skipbw)] = skip_choice
    if request.method == 'POST':
        formset = SkipFormSet(
            request.POST,
            request.FILES,
            initial=initial_skips,
        )
        if formset.is_valid():
            to_skip = []
            to_unskip = []
            for row in formset.cleaned_data:
                skipbw = row['id']
                if row['skipped'] != valid_dates[skipbw]['skipped']:
                    if row['skipped'] is True:
                        to_skip.append(skipbw)
                    else:
                        to_unskip.append(skipbw)
            if not to_skip and not to_unskip:
                messages.add_message(
                    request,
                    messages.ERROR,
                    '''
                    You haven't made any changes to your skip weeks.
                    You can click Cancel if you are happy with your skip
                    weeks as they are.
                    '''
                )
                return redirect(reverse("dashboard_skip_weeks"))
            for skipbw in to_skip:
                assert skipbw not in to_unskip
                skip = Skip(
                    created=now,
                    created_in_billing_week=str(bw),
                    billing_week=skipbw,
                    customer=request.user.customer,
                )
                skip.save()
            for skipbw in to_unskip:
                skip = Skip.objects.filter(
                    customer=request.user.customer,
                    billing_week=skipbw
                ).get()
                skip.delete()
            messages.add_message(
                request,
                messages.SUCCESS,
                'Your skip weeks have been updated successfully'
            )
            return redirect(reverse("dashboard"))
    else:
        formset = SkipFormSet(initial=initial_skips)
    return render(
        request,
        'dashboard/skip-weeks.html',
        {'formset': formset}
    )


def home(request):
    if request.user.username:
        if request.user.is_staff:
            return redirect(reverse("admin:index"))
        return redirect(reverse("dashboard"))
    if request.method == 'GET':
        return render(request, 'home.html')
    elif request.method == 'POST':
        if request.POST.get('join-scheme', False):
            # If they've clicked this button again rather than using back,
            # they probably want to start again:
            request.session.clear()
            return redirect(reverse("join_choose_bags"))
        elif request.POST.get('login', False):
            return redirect(reverse("account_login"))
    return HttpResponseBadRequest()


def join(request):
    return redirect(reverse("join_choose_bags"))


def user_not_signed_in(func):
    def _decorated(request, *args, **kwargs):
        if request.user.username:
            return HttpResponse(
                ERROR_TEMPLATE.format(
                    heading='''
                        You cannot join if you are already a signed in user
                    ''',
                    message='''
                        To change your order or collection point,
                        please <a href="{}">visit the dashboard</a>.
                    '''.format(reverse("dashboard")),
                )
            )
        return func(request, *args, **kwargs)
    return _decorated


def valid_collection_point_in_session(func):
    def _decorated(request, *args, **kwargs):
        if not request.session.get('collection_point'):
            return HttpResponse(
                ERROR_TEMPLATE.format(
                    heading='You must choose a collection point',
                    message='''
                        Please <a href="{}">go back and choose one</a>.
                    '''.format(reverse("join_collection_point")),
                )
            )
        cps = CollectionPoint.objects.filter(
            id__in=[request.session['collection_point']],
            active=True
        ).all()
        if not len(cps) == 1:
            return HttpResponse(
                ERROR_TEMPLATE.format(
                    heading='Your chosen collection point is not available',
                    message='''
                        Please
                        <a href="{}">go back and choose a different one</a>.
                    '''.format(reverse("join_collection_point")),
                )
            )
        return func(request, *args, **kwargs)
    return _decorated


def valid_bag_type_in_session(func):
    def _decorated(request, *args, **kwargs):
        if not sum(request.session.get('bag_type', {}).values()) >= 1:
            return HttpResponse(
                ERROR_TEMPLATE.format(
                    heading='You have not chosen any bags',
                    message='''
                        Please
                        <a href="{}">go back and choose at least one</a>.
                    '''.format(reverse("join_choose_bags"))
                )
            )
        current_bag_types = BagType.objects.order_by(
            'display_order'
        ).filter(
            active=True,
            id__in=[int(x) for x in request.session['bag_type'].keys()]
        )
        if len(current_bag_types) != len(request.session['bag_type']):
            return HttpResponse(
                ERROR_TEMPLATE.format(
                    heading='Not all of your bag choices are available',
                    message='''
                        Please
                        <a href="{}">go back and update your order</a>.
                    '''.format(reverse("join_choose_bags"))
                )
            )
        return func(request, *args, **kwargs)
    return _decorated


@user_not_signed_in
@valid_bag_type_in_session
@valid_collection_point_in_session
def signup(request):
    return allauth_signup(request)


@user_not_signed_in
def choose_bags(request):
    OrderFormSet = formset_factory(
        QuantityForm,
        extra=0,
        formset=BaseOrderFormSet,
    )
    choices = []
    available_bag_types = BagType.objects.order_by(
        'display_order'
    ).filter(active=True)
    for bag_type in available_bag_types:
        choices.append({
            "id": bag_type.id,
            "name": bag_type.name,
            "weekly_cost": bag_type.weekly_cost,
            "quantity": request.session.get(
                'bag_type', {}).get(str(bag_type.id), 0),
        })
    if request.method == 'POST':
        formset = OrderFormSet(
            request.POST,
            request.FILES,
            initial=choices,
        )  # auto_id=False)
        if formset.is_valid():
            chosen_bag_type = {}
            available_bag_types = BagType.objects.order_by(
                'display_order'
            ).filter(active=True)
            for bag_type in available_bag_types:
                for row in formset.cleaned_data:
                    if bag_type.id == row['id'] and row['quantity'] != 0:
                        chosen_bag_type[bag_type.id] = row['quantity']
            request.session['bag_type'] = chosen_bag_type
            return redirect(reverse("join_collection_point"))
    else:
        formset = OrderFormSet(initial=choices)
    return render(request, 'choose_bags.html', {'formset': formset})


@user_not_signed_in
@valid_bag_type_in_session
def collection_point(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CollectionPointForm(request.POST)
        # XXX Guessing this checks the actual IDs too?
        if form.is_valid():
            request.session['collection_point'] = \
                form.cleaned_data['collection_point'].id
            return redirect(reverse("account_signup"))
    # if a GET (or any other method) we'll create a blank form
    else:
        form = CollectionPointForm(
            initial={
                'collection_point': request.session.get('collection_point')
            }
        )
    locations = {}
    for i, collection_point in enumerate(
        form.fields['collection_point'].queryset.all()
    ):
        locations['id_collection_point_{}'.format(i)] = {
            "longitude": escape(collection_point.longitude),
            "latitude": escape(collection_point.latitude),
        }
    return render(
        request,
        'collection_point.html',
        {'form': form, 'locations': json.dumps(locations)}
    )


class _RF:
    """Used as an empty attribute container in dashboard_gocardless()"""
    pass


@login_required
@not_staff
@gocardless_is_not_set_up
def dashboard_gocardless(request):
    if request.method == 'POST':
        assert request.user.username
        # from django.contrib.sites.models import Site
        # current_site = Site.objects.get_current()
        # success_redirect_url = 'http://{}{}'.format(
        #     current_site.domain,
        #     reverse('gocardless_callback'),
        # )
        session_token = str(uuid.uuid4())
        success_redirect_url = '{}://{}{}'.format(
            request.scheme,
            request.META['HTTP_HOST'],
            reverse('gocardless_callback'),
        )
        try:
            redirect_flow = gocardless_client.redirect_flows.create(params={
                'description': 'Your Growing Communities Veg Box Order',
                'session_token': session_token,
                'success_redirect_url': success_redirect_url,
                # 'scheme': ... DD scheme.
            })
        except:
            if not settings.TIME_TRAVEL:
                raise
            else:
                offline_mode = True
                redirect_flow = _RF()
                redirect_flow.id = str(uuid.uuid4())
        else:
            offline_mode = False
        mandate = BillingGoCardlessMandate(
            session_token=session_token,
            gocardless_redirect_flow_id=redirect_flow.id,
            customer=request.user.customer,
        )
        mandate.save()
        if offline_mode:
            return HttpResponse('Offline, did not set up mandate')
        else:
            return redirect(redirect_flow.redirect_url)
    else:
        return render(request, 'dashboard/set-up-go-cardless.html')


@login_required
@not_staff
@gocardless_is_not_set_up
def gocardless_callback(request):
    if settings.GOCARDLESS_ENVIRONMENT == 'sandbox' and \
       request.GET.get('skip', '').lower() == 'true':
        mandate = BillingGoCardlessMandate.objects.filter(
            customer=request.user.customer,
        ).get()
        mandate.gocardless_mandate_id = str(uuid.uuid4())
    else:
        mandate = BillingGoCardlessMandate.objects.filter(
            customer=request.user.customer,
            gocardless_redirect_flow_id=request.GET['redirect_flow_id'],
        ).get()
        complete_redirect_flow = gocardless_client.redirect_flows.complete(
            mandate.gocardless_redirect_flow_id,
            {'session_token': mandate.session_token}
        )
        assert complete_redirect_flow.id == mandate.gocardless_redirect_flow_id
        mandate.gocardless_mandate_id = complete_redirect_flow.links.mandate
    mandate.in_use_for_customer = request.user.customer
    mandate.save()
    now = timezone.now()
    bw = get_billing_week(now)
    account_status_change = AccountStatusChange(
        changed=now,
        changed_in_billing_week=str(bw),
        customer=request.user.customer,
        status=AccountStatusChange.ACTIVE,
    )
    account_status_change.save()
    tags = CustomerTag.objects.filter(tag='Starter').all()
    if tags:
        request.user.customer.tags.add(tags[0])
    messages.add_message(
        request,
        messages.INFO,
        'Successfully set up Go Cardless.'
    )
    request.user.customer.save()
    return redirect(reverse("dashboard"))


@login_required
@not_staff
@gocardless_is_set_up
def dashboard(request):
    if request.user.customer.account_status != AccountStatusChange.LEFT:
        latest_cp_change = CustomerCollectionPointChange.objects.order_by(
            '-changed'
        ).filter(customer=request.user.customer)[:1]
        latest_customer_order_change = CustomerOrderChange.objects.order_by(
            '-changed'
        ).filter(customer=request.user.customer)[:1]
        collection_point = latest_cp_change[0].collection_point
        now = timezone.now()
        bw = get_billing_week(now)
        weekday = now.weekday()
        skipped_billing_weeks = []
        skipped = len(
            Skip.objects.order_by('billing_week').filter(
                customer=request.user.customer,
                billing_week=str(bw),
            ).all()
        ) > 0
        if weekday == 6:  # Sunday
            if collection_point.collection_day == 'WED':
                collection_date = 'Wednesday'
            elif collection_point.collection_day == 'THURS':
                collection_date = 'Thursday'
            else:
                collection_date = 'Wednesday and Thursday'
            if timezone.now().hour < bw.end.hour:
                deadline = '3pm today'
                changes_affect = "next week's collection"
            else:
                deadline = '3pm next Sunday'
                changes_affect = "the collection after next"
        elif weekday == 0:  # Monday
            if collection_point.collection_day == 'WED':
                collection_date = 'Wednesday'
            elif collection_point.collection_day == 'THURS':
                collection_date = 'Thursday'
            else:
                collection_date = 'Wednesday and Thursday'
            deadline = '3pm this Sunday'
            changes_affect = "next week's collection"
        elif weekday == 1:  # Tuesday
            if collection_point.collection_day == 'WED':
                collection_date = 'tomorrow'
            elif collection_point.collection_day == 'THURS':
                collection_date = 'Thursday'
            else:
                collection_date = 'tomorrow and Thursday'
            deadline = '3pm this Sunday'
            changes_affect = "next week's collection"
        elif weekday == 2:  # Wednesday
            if collection_point.collection_day == 'WED':
                collection_date = 'today'
            elif collection_point.collection_day == 'THURS':
                collection_date = 'tomorrow'
            else:
                collection_date = 'today and tomorrow'
            deadline = '3pm this Sunday'
            changes_affect = "next week's collection"
        elif weekday == 3:  # Thurs
            if collection_point.collection_day == 'WED':
                collection_date = 'Wednesday next week'
            elif collection_point.collection_day == 'THURS':
                collection_date = 'today'
            else:
                collection_date = 'today'
            deadline = '3pm this Sunday'
            changes_affect = "next week's collection"
        else:
            if collection_point.collection_day == 'WED':
                collection_date = 'Wednesday next week'
            elif collection_point.collection_day == 'THURS':
                collection_date = 'Thursday next week'
            else:
                collection_date = 'Wednesday and Thursday next week'
            if weekday == 4:  # Friday
                deadline = '3pm this Sunday'
            else:  # Saturday
                deadline = '3pm tomorrow'
            changes_affect = "next week's collection"
        bag_quantities = CustomerOrderChangeBagQuantity.objects.filter(
            customer_order_change=latest_customer_order_change
        ).all()
        if skipped:
            collection_date = collection_date.replace(' and ', ' or ')
            if not (collection_date.startswith('today') or collection_date.startswith('tomorrow')):
                collection_date = 'on '+collection_date
        return render(
            request,
            'dashboard/index.html',
            {
                'bag_quantities': bag_quantities,
                'collection_point': collection_point,
                'collection_date': collection_date,
                'deadline': deadline,
                'changes_affect': changes_affect,
                'skipped': skipped,
            }
        )
    else:
        return render(
            request,
            'dashboard/re-join-scheme.html',
        )


@login_required
@not_staff
@gocardless_is_set_up
def dashboard_change_order(request):
    if request.method == 'POST' and request.POST.get('cancel'):
        messages.add_message(
            request,
            messages.INFO,
            'Your order has not been changed.'
        )
        return redirect(reverse("dashboard"))
    OrderFormSet = formset_factory(
        QuantityForm,
        extra=0,
        formset=BaseOrderFormSet,
    )
    initial_bag_quantities = {}
    for bag_quantity in request.user.customer.bag_quantities:
        initial_bag_quantities[bag_quantity.bag_type.id] =\
            bag_quantity.quantity
    available_bag_types = BagType.objects.order_by('display_order')
    bag_type_ids = [b.id for b in available_bag_types]
    active_bag_types = []
    for bag_type in available_bag_types:
        if bag_type.active:
            active_bag_types.append({
                "id": bag_type.id,
                "name": bag_type.name,
                "weekly_cost": bag_type.weekly_cost,
                "quantity": 0,
                "not_active_warning_needed": False,
            })
    active_bag_type_ids = [bt['id'] for bt in active_bag_types]
    if request.method == 'POST':
        formset = OrderFormSet(
            request.POST,
            request.FILES,
            initial=active_bag_types,
        )
        if formset.is_valid():
            bag_quantities = {}
            for row in formset.cleaned_data:
                # XXX Django should take care of making sure the IDs are in
                #     the initial data?
                # bag ID not active and the quantity you are asking for is
                # greater than what you started with
                if row['id'] not in bag_type_ids:
                    raise Exception(
                        'Invalid bag type ID: {}'.format(row['id'])
                    )
                if row['id'] not in active_bag_type_ids:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        'One or more bags you selected is no longer available.'
                    )
                    return redirect(reverse("dashboard_change_order"))
                if row['quantity'] != 0:
                    bag_quantities[row['id']] = row['quantity']
            # Save and load bag types
            if initial_bag_quantities == bag_quantities:
                messages.add_message(
                    request,
                    messages.ERROR,
                    '''
                    You haven't made any changes to your order.
                    You can click Cancel if you are happy with your order as
                    it is.
                    '''
                )
                return redirect(reverse("dashboard_change_order"))
                # return render(
                #     request,
                #     'dashboard/change-order.html',
                #     {'formset': formset}
                # )
            request.user.customer.bag_quantities = bag_quantities
            messages.add_message(
                request,
                messages.SUCCESS,
                'Your order has been updated successfully'
            )
            return redirect(reverse("dashboard"))
    else:
        formset = OrderFormSet(initial=active_bag_types)
    return render(
        request,
        'dashboard/change-order.html',
        {'formset': formset}
    )


@login_required
@not_staff
@gocardless_is_set_up
def dashboard_change_collection_point(request):
    if request.method == 'POST' and request.POST.get('cancel'):
        messages.add_message(
            request,
            messages.INFO,
            'Your collection point has not been changed.'
        )
        return redirect(reverse("dashboard"))
    current_collection_point = request.user.customer.collection_point
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CollectionPointForm(request.POST)
        # XXX Guessing this checks the actual IDs too?
        if form.is_valid():
            if form.cleaned_data['collection_point'].id == \
               request.user.customer.collection_point.id:
                messages.add_message(
                    request,
                    messages.ERROR,
                    '''
                    You haven't made any changes to your collection point.
                    You can click Cancel if you are happy with your
                    current collection point.
                    '''
                )
                return render(
                    request,
                    'dashboard/change-collection-point.html',
                    {
                        'form': form,
                        'current_collection_point': current_collection_point,
                    }
                )
            request.user.customer.collection_point = \
                form.cleaned_data['collection_point'].id
            messages.add_message(
                request,
                messages.SUCCESS,
                'Your collection point has been updated successfully'
            )
            return redirect(reverse("dashboard"))
    # if a GET (or any other method) we'll create a blank form
    else:
        form = CollectionPointForm(
            initial={
                'collection_point': request.user.customer.collection_point.id
            }
        )
    locations = {}
    for i, collection_point in enumerate(
        form.fields['collection_point'].queryset.all()
    ):
        locations['id_collection_point_{}'.format(i)] = {
            "longitude": escape(collection_point.longitude),
            "latitude": escape(collection_point.latitude),
        }
    return render(
        request,
        'dashboard/change-collection-point.html',
        {
            'form': form,
            'locations': json.dumps(locations),
            'current_collection_point': current_collection_point,
        }
    )


def logged_out(request):
    if request.user.username:
        return redirect(reverse("account_logout"))
    return render(
        request,
        'account/logged_out.html',
    )


@login_required
@not_staff
@gocardless_is_set_up
def bank_details(request):
    return render(request, 'dashboard/bank-details.html')


LEAVE_REASON_CHOICES = (
    ('moving', 'Moving away from the area'),
)


# class FutureDateField(forms.DateField):
#     def clean(self, value):
#         if value < timezone.today().strftime('%Y-%m-%d'):
#             raise forms.ValidationError(
#                 "Please choose a leaving date that isn't in the past."
#             )
#         value = super().clean(value)
#         return value


class LeaveReasonForm(forms.Form):
    reason = forms.ChoiceField(
        label='Reason',
        choices=LEAVE_REASON_CHOICES,
        required=False,
    )
    comments = forms.CharField(
        label='Any other comments?',
        widget=forms.Textarea,
        required=False,
    )
    # leaving_date = FutureDateField(
    #     initial=timezone.today,
    #     widget=forms.SelectDateWidget(),
    # )


@login_required
@not_staff
@gocardless_is_set_up
@have_not_left_scheme
def dashboard_leave(request):
    if request.method == 'POST' and request.POST.get('cancel'):
        messages.add_message(
            request,
            messages.INFO,
            'You are still part of the scheme, and haven\'t left.'
        )
        return redirect(reverse("dashboard"))
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = LeaveReasonForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            reason = dict(form.fields['reason'].choices)[
                form.cleaned_data['reason']
            ]
            a = send_mail(
                '[BlueWorld] Leaver Notification',
                '''
                Hello from BlueWorldLite,

                {} has decided to leave the scheme. Here are the details:

                Reason: {}\n
                Comments:
                {}

                Thanks,

                The BlueWorldLite system
                '''.format(
                    request.user.customer.full_name,
                    reason,
                    form.cleaned_data['comments'],
                ),
                settings.DEFAULT_FROM_EMAIL,
                settings.LEAVER_EMAIL_TO,
                fail_silently=False,
            )
            # Only save changes now in case there is a problem with the email
            now = timezone.now()
            bw = get_billing_week(now)
            account_status_change = AccountStatusChange(
                changed=now,
                changed_in_billing_week=str(bw),
                customer=request.user.customer,
                status=AccountStatusChange.LEFT,
            )
            account_status_change.save()
            return redirect(reverse('dashboard_bye'))
    # if a GET (or any other method) we'll create a blank form
    else:
        form = LeaveReasonForm()
    return render(
        request,
        'dashboard/leave.html',
        {
            'form': form,
        }
    )


@login_required
@not_staff
@have_left_scheme
def dashboard_bye(request):
    return render(request, 'dashboard/bye.html')


if settings.TIME_TRAVEL:
    freezer = None

    def timetravel_to(request, date):
        global freezer
        if freezer is not None:
            freezer.stop()
        freezer = freezegun.freeze_time(date, tick=True)
        freezer.start()
        return HttpResponse('ok')

    def timetravel_freeze(request, date):
        global freezer
        if freezer is not None:
            freezer.stop()
        freezer = freezegun.freeze_time(date)
        freezer.start()
        return HttpResponse('ok')

    def timetravel_cancel(request):
        global freezer
        if freezer is None:
            return HttpResponse('not time travelling')
        freezer.stop()
        freezer = None
        return HttpResponse('ok')


def get_minute(start):
    current_year = start.year
    current_month = start.month
    current_day = start.day
    current_hour = start.hour
    current_minute = start.minute
    return datetime.datetime(
        current_year,
        current_month,
        current_day,
        current_hour,
        current_minute,
        0,
        tzinfo=timezone.get_default_timezone()
    )


def get_month(start):
    current_year = start.year
    current_month = start.month
    return datetime.datetime(
        current_year,
        current_month,
        1,
        0, 0, 0,
        tzinfo=timezone.get_default_timezone()
    )


def _add_change(changes, change):
    change_month = get_month(change[0])
    # if change_month.month == 12:
    #     change_month = change_month.replace(year=change_month.year + 1, month=1)
    # else:
    #     change_month = change_month.replace(month=change_month.month + 1)
    if change_month not in changes:
        changes[change_month] = OrderedDict()
    change_minute = get_minute(change[0])
    if change_minute not in changes[change_month]:
        changes[change_month][change_minute] = []
    changes[change_month][change_minute].append(change)


def get_order_history_events(customer):
    # date, code, description, collection_affected, billing_month_affected, detail
    # So: pretty much everything affexts the billing month after the next invoicing date
    #      e.g. make change on 5th July, greater than 3rd july < 31st July => Affects August

    # Display by
    # find_billing_month_affected()


    # This is going to get events by month, but we don't want to show changes that haven't been billed yet
    # So, if we are in July and make changes, those changes aren't relevant until August.
    # This means we display them against the next month.
    created = None
    changes = []
    for order_change in CustomerOrderChange.objects.filter(customer=customer).order_by('-changed'):
        if not created:
             created = order_change.changed
        changes.append((order_change.changed, 'ORDER_CHANGE', render_bag_quantities(order_change.bag_quantities.all())))
    for collection_point_change in CustomerCollectionPointChange.objects.filter(customer=customer).order_by('-changed'):
        changes.append((collection_point_change.changed, 'COLLECTION_POINT_CHANGE', collection_point_change.collection_point.name))
    for account_status_change in AccountStatusChange.objects.filter(customer=customer).order_by('-changed'):
        changes.append((account_status_change.changed, 'ACCOUNT_STATUS_CHANGE', account_status_change.get_status_display()))
    for skip in Skip.objects.filter(customer=customer, created__lt=timezone.now()).order_by('-created'):
        changes.append(
            (
                skip.created,
                'SKIP_WEEK',
                'Week commencing {}'.format(
                    formats.date_format(parse_billing_week(skip.billing_week).mon, "DATE_FORMAT"),
                )
            )
        )

    # Get pickup dates since the account was created
    pd = get_pickup_dates(created, timezone.now())
    # import pdb; pdb.set_trace()
    res = OrderedDict()
    for change in sorted(changes):
        _add_change(res, change)

    # Now, for each month in
    # XXX Perhaps should be < last billing date

    return created, res


@login_required
@not_staff
@gocardless_is_set_up
def dashboard_order_history(request):
    created, order_history = get_order_history_events(request.user.customer)
    return render(
        request,
        'dashboard/order-history.html',
        {
            'created': created,
            'order_history': order_history,
        }
    )


@login_required
@not_staff
@gocardless_is_set_up
def dashboard_billing_history(request):
    created, billing_history = get_order_history_events(request.user.customer)
    return render(
        request,
        'dashboard/billing-history.html',
        {
            'created': created,
            'billing_history': billing_history,
        }
    )


@login_required
@not_staff
@gocardless_is_set_up
@have_left_scheme
def dashboard_rejoin_scheme(request):
    if request.method == 'POST':
        now = timezone.now()
        bw = get_billing_week(now)
        account_status_change = AccountStatusChange(
            changed=now,
            changed_in_billing_week=str(bw),
            customer=request.user.customer,
            status=AccountStatusChange.ACTIVE,
        )
        account_status_change.save()
        messages.add_message(
            request,
            messages.INFO,
            'Successfully re-activated your account',
        )
        return redirect(reverse("dashboard"))
    else:
        return HttpResponseBadRequest()


def gocardless_events_callback(request):
    # XXX import pdb; pdb.set_trace()
    pass


def billing_dates(request):
    pickup_dates = get_pickup_dates(start_of_the_month(timezone.now().year, timezone.now().month), 52, month_start=True)
    billing_dates = OrderedDict()
    for month in pickup_dates:
        billing_dates[month] = pickup_dates[month][0].start
    return render(
        request,
        'billing-dates.html',
        {
            'pickup_dates': pickup_dates,
            'billing_dates': billing_dates,
        }
    )
