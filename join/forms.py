from django import forms
from .models import (
    AccountStatusChange,
    Customer,
    CustomerCollectionPointChange,
    CustomerOrderChange,
    CustomerOrderChangeBagQuantity,
)


class SignupForm(forms.Form):
    full_name = forms.CharField(max_length=255, label='Full name', help_text="We'll use this to label your bag when you pick it up")
    nickname = forms.CharField(max_length=30, label='What should we call you?', help_text="We'll use this when emailing you about the scheme.")
    mobile = forms.CharField(max_length=30, label='Mobile', required=False, help_text="We use this to notify when your bag is ready to pick up")

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
