from decimal import Decimal

from django.test import Client
from django.core.urlresolvers import reverse

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from .factories import (
    CustomerFactory, BagTypeFactory, CollectionPointFactory,
    AccountStatusChangeFactory, CompleteGoCardlessMandateFactory,
    GoCardlessMandateFactory
)

from .models import AccountStatusChange, CustomerTag


class UserWantsToLeaveSchemeTestCase(StaticLiveServerTestCase):
    """
    We set up a user, with:
        a collection point,
        an order, of a given bag type and quantity
        a complete mandate

    They sign in and request to leave.

    We want to test:
        they have the correct tag applied
        their dashboard is showing something different
        they don't have collection beyond their leave date
        they don't see collections beyond their date
        a reminder exists for the correct date
        they can rejoin

    """


    def setUp(self):

        veg_bag_price = Decimal(16.25)
        large_veg = BagTypeFactory()
        # TODO
        large_veg.weekly_cost = veg_bag_price
        large_veg.save()
        # now we have a user, we need to

        col_point = CollectionPointFactory()

        customer = CustomerFactory(full_name="Joe Bloggs")
        customer.save()
        user = customer.user

        start_status = AccountStatusChangeFactory(customer=customer,
            status=AccountStatusChange.AWAITING_DIRECT_DEBIT)

        customer.collection_point = col_point
        customer._set_bag_quantities({large_veg.id: 1})

        # presumably, we have this
        complete_mandate = CompleteGoCardlessMandateFactory(customer=customer,
            amount_notified=veg_bag_price)

        # you can have more than one mandate for a user, but we should only
        # have one mandate in use at a given time
        complete_mandate.in_use_for_customer=customer
        complete_mandate.save()
        customer.save()


        assert(customer.user.username == customer.full_name.lower().split(' ')[0])
        assert(customer.account_status == AccountStatusChange.AWAITING_DIRECT_DEBIT)
        assert(customer.gocardless_current_mandate)

        self.client = Client()
        self.customer = customer

        # are we logged in? not sure if we can use the client.login() method
        # with allauth

        # why would logging in with an email address trigger it existing on a user?
        self.creds = {'login': 'joe@example.com', 'password': 'password'}
        res = self.client.post(reverse("account_login"), self.creds)

        assert(len(self.customer.user.emailaddress_set.all()) > 0 )
        email = self.customer.user.emailaddress_set.all().first()
        email.verified = True
        email.save()
        self.customer.user.save()

        leaving_tag = CustomerTag(tag='Leaving')
        leaving_tag.save()

        assert(len(CustomerTag.objects.filter(tag='Leaving')) > 0)

    def test_leaving_tag_is_applied(self):
        # log us in
        login_res = self.client.post(reverse("account_login"), self.creds)

        leave_get = self.client.get(reverse("dashboard_leave"), follow=True)

        leaving_reasons = {
            'reason': 'hard_to_pickup',
            'comments': "It's difficult getting there in time."
        }

        leave_post = self.client.post(reverse('dashboard_leave'),
            leaving_reasons)

        leaving_tag = CustomerTag.objects.get(tag='Leaving')

        assert(leaving_tag in self.customer.tags.all())

    def test_reminder_is_created(self):

        # log us in
        login_res = self.client.post(reverse("account_login"), self.creds)
        leave_get = self.client.get(reverse("dashboard_leave"), follow=True)

        leaving_reasons = {
            'reason': 'hard_to_pickup',
            'comments': "It's difficult getting there in time."
        }
        leave_post = self.client.post(reverse('dashboard_leave'),
            leaving_reasons)

        # this has to be the week before the billing week ends
        Reminder.objects.filter(customer=self.customer )
