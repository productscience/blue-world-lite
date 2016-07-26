from django import forms
from .models import (
    AccountStatusChange,
    Customer,
    CustomerCollectionPointChange,
    CustomerOrderChange,
    CustomerOrderChangeBagQuantity,
)


class SignupForm(forms.Form):
    full_name = forms.CharField(max_length=255, label='Full name')
    nickname = forms.CharField(max_length=30, label='What should we call you?')
    mobile = forms.CharField(max_length=30, label='Mobile', required=False)

    def signup(self, request, user):
        customer = Customer(
            full_name=self.cleaned_data['full_name'],
            nickname=self.cleaned_data['nickname'],
            mobile=self.cleaned_data['mobile'],
            user=user,
        )
        customer.save()
        account_status_change = AccountStatusChange(
            customer=customer,
            status=AccountStatusChange.AWAITING_DIRECT_DEBIT,
        )
        account_status_change.save()
        customer.collection_point = request.session['collection_point']
        customer.bag_quantities = request.session['bag_type']
