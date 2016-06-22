from django import forms
from .models import Customer, CollectionPointChange, OrderChange, BagQuantity


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
        collection_point_change = CollectionPointChange(
            customer=customer,
            collection_point_id=request.session['collection_point'],
        )
        collection_point_change.save()
        order_change = OrderChange(customer=customer)
        order_change.save()
        for bag_type_id, quantity in request.session['bag_type'].items():
            bag_quantity = BagQuantity(order_change=order_change, bag_type_id=bag_type_id, quantity=quantity)
            bag_quantity.save()
