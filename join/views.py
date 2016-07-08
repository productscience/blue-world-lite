import json
import datetime

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
from django.utils.html import format_html, escape
import freezegun

from .models import (
    AccountStatusChange,
    BagType,
    CollectionPoint,
    Customer,
    CustomerCollectionPointChange,
    CustomerOrderChange,
    CustomerOrderChangeBagQuantity,
)


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
                last_bag = form.cleaned_data['id']
        # Do we want to validate this?
        if total_bags < 1:
            raise forms.ValidationError(
                "Please choose at least one bag to order."
            )
        if total_bags == 1 and last_bag == 3:
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
        if not request.user.customer.go_cardless:
            return render(request, 'dashboard/set-up-go-cardless.html')
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
        bag_quantities = CustomerOrderChangeBagQuantity.objects.filter(
            customer_order_change=latest_customer_order_change
        ).all()
        return render(
            request,
            'dashboard/index.html',
            {
                'collection_point': latest_cp_change[0].collection_point,
                'bag_quantities': bag_quantities,
                'next_collection': next_collection(),
                'next_deadline': next_deadline(),
                'timenow': datetime.datetime.now(),
            }
        )
    else:
        return render(
            request,
            'dashboard/re-join-scheme.html',
        )


@login_required
@not_staff
def go_cardless_callback(request):
    if request.user.customer.go_cardless:
        return HttpResponseForbidden(
            FORBIDDEN_TEMPLATE.format(
                heading='Already set up',
                message=''
            )
        )
    request.user.customer.go_cardless = 'done'
    request.user.customer.save()
    account_status_change = AccountStatusChange(
        customer=request.user.customer,
        status=AccountStatusChange.ACTIVE,
    )
    account_status_change.save()
    messages.add_message(
        request,
        messages.INFO,
        'Successfully set up Go Cardless.'
    )
    return redirect(reverse("dashboard"))


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
        formset = OrderFormSet(request.POST, request.FILES, initial=active_bag_types)
        if formset.is_valid():
            bag_quantities = {}
            for row in formset.cleaned_data:
                # XXX Django should take care of making sure the IDs are in
                #     the initial data?
                # bag ID not active and the quantity you are asking for is
                # greater than what you started with
                if row['id'] not in bag_type_ids:
                    raise Exception('Invalid bag type ID: {}'.format(row['id']))
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
            account_status_change = AccountStatusChange(
                customer=request.user.customer,
                status=AccountStatusChange.LEFT,
            )
            account_status_change.save()
            return redirect(reverse('dashboard_bye'))
    # if a GET (or any other method) we'll create a blank form
    else:
        form = LeaveReasonForm()
    return render(request, 'dashboard/leave.html', {'form': form})


@login_required
@not_staff
@have_left_scheme
def dashboard_bye(request):
    return render(request, 'dashboard/bye.html')


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


def next_deadline():
    sunday = 6
    return _next_weekday(datetime.datetime.now(), sunday, 15).replace(
        hour=15,
        minute=00,
        second=0,
        microsecond=0
    )


def next_collection():
    wednesday = 2
    a = _next_weekday(datetime.datetime.now(), wednesday, 12)
    return a


def _next_weekday(d, weekday, cutoff_hour):
    # The value of weekday is 0-6 where Monday is 0 and Sunday is 6
    days_ahead = weekday - d.weekday()
    if days_ahead == 0:
        if d.hour >= cutoff_hour:
            days_ahead += 7
    elif days_ahead < 0:  # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


@login_required
@not_staff
@gocardless_is_set_up
def dashboard_order_history(request):
    return render(request, 'dashboard/order-history.html')


@login_required
@not_staff
@gocardless_is_set_up
@have_left_scheme
def dashboard_rejoin_scheme(request):
    if request.method == 'POST':
        account_status_change = AccountStatusChange(
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
