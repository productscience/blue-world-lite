
from decimal import Decimal

from django.test import TestCase
from django.test import Client


from django.utils import timezone

from allauth.utils import get_user_model, get_current_site
# we want two collection points

from .models import CollectionPoint

# we also want at least one user
from .models import (CollectionPoint, CustomerOrderChangeBagQuantity,
    CustomerOrderChange, Customer, AccountStatusChange, BagType, CollectionPoint)


from billing_week import get_billing_week




class TestCollectionsShowsRightBillingWeeks(TestCase):

    @classmethod
    def setUpTestData(self):


        self.user = get_user_model().objects.create(username="joe", email="joe@example.com", password="sekrit")

        now = timezone.now()
        bw = get_billing_week(now)

        self.joe = Customer(
            created=now,
            created_in_billing_week=str(bw),
            full_name="Joseph Bloggs",
            nickname="Joe",
            user=self.user
        )

        self.joe.save()

        small_bags = BagType.objects.create(name="Med Veg", active=True)
        small_bags.weekly_cost = Decimal('9.00')
        small_bags.save()

        ofs = CollectionPoint.objects.create(
            location='61 Leswin Road, N16 7NX',
            collection_day='WED',
            active=True,
            name='The Old Fire Station')

        ofs.save()

        self.joe.collection_point = ofs
        self.joe._set_bag_quantities({small_bags.id: 1})

        account_status_change = AccountStatusChange(
            changed=now,
            changed_in_billing_week=str(bw),
            customer=self.joe,
            status=AccountStatusChange.ACTIVE,
        ).save()




    def test_dates_of_collections(self):

        response = self.client.post('/login', { 'login':'joe@example.com', 'password':'sekrit'})



        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        # import ptpdb; ptpdb.set_trace()

        # Check that the rendered context contains 5 customers.
        # self.assertEqual(len(response.context['customers']), 5)
        #
        #
