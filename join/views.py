from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from .models import CollectionPoint, BagType, Customer, CollectionPointChange, OrderChange, BagQuantity
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from allauth.account.views import signup as allauth_signup

from django.utils.html import format_html
from django import forms
from django.forms import formset_factory
from django.forms import BaseFormSet


class QuantityForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(min_value=0, max_value=100, widget=forms.widgets.TextInput())


class BaseOrderFormSet(BaseFormSet):
    def clean(self):
        """Checks that at least one bag has been ordered"""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        total_bags = 0
        for form in self.forms:
            total_bags += form.cleaned_data['quantity']
        # Do we want to validate this?
        if total_bags < 1:
            raise forms.ValidationError("Please choose at least one bag to order.")


class CollectionPointModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if obj.location:
            return format_html("{} <small>{}</small>", obj.name, obj.location)
        else:
            return format_html("{}", obj.name)


class CollectionPointForm(forms.Form):
    collection_point = CollectionPointModelChoiceField(
        queryset=CollectionPoint.objects.order_by('display_order').filter(active=True),
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
            # If they've clicked this button again rather than using back, they probably want to start again:
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
            return HttpResponse('<html><h3>You cannot join if you are already a signed in user</h3> <p>To change your order or collection point, please <a href="{}">visit the dashboard</a>.</p></html>'.format(reverse("dashboard")))
        return func(request, *args, **kwargs)
    return _decorated


def valid_collection_point_in_session(func):
    def _decorated(request, *args, **kwargs):
        if not request.session.get('collection_point'):
            return HttpResponse('<html><h3>You must choose a collection point</h3> <p>Please <a href="{}">go back and choose one</a>.</p></html>'.format(reverse("join_collection_point")))
        return func(request, *args, **kwargs)
    return _decorated

def valid_bag_type_in_session(func):
    def _decorated(request, *args, **kwargs):
        if not sum(request.session.get('bag_type', {}).values()) >= 1:
            return HttpResponse('<html><h3>You have not chosen any bags</h3> <p>Please <a href="{}">go back and choose at least one</a>.</p></html>'.format(reverse("join_choose_bags")))
        current_bag_types = BagType.objects.order_by('display_order').filter(active=True, id__in=[int(x) for x in request.session['bag_type'].keys()])
        if len(current_bag_types) != len(request.session['bag_type']):
            return HttpResponse('<html><h3>Not all of your bag choices are available</h3> <p>Please <a href="{}">go back and update your order</a>.</p></html>'.format(reverse("join_choose_bags")))
        return func(request, *args, **kwargs)
    return _decorated


@user_not_signed_in
@valid_bag_type_in_session
@valid_collection_point_in_session
def signup(request):
    return allauth_signup(request)

# import allauth.account.signals
# from django.dispatch import receiver
# from django.contrib.auth.models import User
#
#
# @receiver(allauth.account.signals.user_signed_up, sender=User)
# def on_signup(request, user, **kwargs):
#     pass
#     # import pdb; pdb.set_trace()
#     # Serialise session
#




# A successful signup fires this trigger which we use to save the user's session choices.
# allauth.account.signals.user_signed_up(request, user)


@user_not_signed_in
def choose_bags(request):
    OrderFormSet = formset_factory(QuantityForm, extra=0, formset=BaseOrderFormSet)
    choices = []
    available_bag_types = BagType.objects.order_by('display_order').filter(active=True)
    for bag_type in available_bag_types:
        choices.append({
            "id": bag_type.id,
            "name": bag_type.name,
            "weekly_cost": bag_type.weekly_cost,
            "quantity": request.session.get('bag_type', {}).get(str(bag_type.id), 0),
        })
    if request.method == 'POST':
        formset = OrderFormSet(request.POST, request.FILES, initial=choices) # auto_id=False)
        if formset.is_valid():
            chosen_bag_type = {}
            available_bag_types = BagType.objects.order_by('display_order').filter(active=True)
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
            request.session['collection_point'] = form.cleaned_data['collection_point'].id
            return redirect(reverse("account_signup"))
    # if a GET (or any other method) we'll create a blank form
    else:
        form = CollectionPointForm(initial={'collection_point': request.session.get('collection_point')})
    return render(request, 'collection_point.html', {'form': form})


@login_required
def dashboard(request):
    if request.user.is_superuser:
        return HttpResponseForbidden('<html><body><h1>Super users don\'t have a dashboard</h1></body></html>')
    if not request.user.customer.go_cardless:
        return HttpResponse('<html><body><h1>Set up Go Cardless</h1><p><a href="{}">Skip</a></p></body></html>'.format(reverse("go_cardless_callback")))


    latest_collection_point_change = CollectionPointChange.objects.order_by('changed').filter(customer=request.user.customer)[:1]
    latest_order_change = OrderChange.objects.order_by('changed').filter(customer=request.user.customer)[:1]
    bag_quantities = BagQuantity.objects.filter(order_change=latest_order_change).all()
    return render(
        request,
        'dashboard.html',
        {
            'collection_point': latest_collection_point_change[0].collection_point,
            'bag_quantities': bag_quantities,
        }
    )


@login_required
def go_cardless_callback(request):
    if request.user.customer.go_cardless:
         return HttpResponseForbidden('<html><body><h1>Already set up</h1></body></html>')
    request.user.customer.go_cardless = 'done'
    request.user.customer.save()
    messages.add_message(request, messages.INFO, 'Successfully set up Go Cardless.')
    return redirect(reverse("dashboard"))


@login_required
def dashboard_change_order(request):
    return HttpResponse('<html><body><h1>Change Order</h1><p>This functionality is not implemented yet</p></body></html>')


@login_required
def dashboard_change_collection_point(request):
    return HttpResponse('<html><body><h1>Change Collection Point</h1><p>This functionality is not implemented yet</p></body></html>')
