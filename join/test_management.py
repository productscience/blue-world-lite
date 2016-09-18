from django.utils.six import StringIO
from django.test import TransactionTestCase
from django.core.management import call_command

from .models import (
    BillingGoCardlessMandate, CollectionPoint, Customer,
    CustomerOrderChange
)

class ImportUserWithManagementTestCase(TransactionTestCase):
    """
    Tests that a customer who has been imported is Class-based
    as an active user, with a working mandate/pre-auth for taking
    payments
    """

    # set up using special import user fixture just for this one
    fixtures = ['data/user.json', 'initial.json']

    def setUp(self):
        #  call management command
        out = StringIO()

        # check we have all our collection points we need for the
        # import, so we know we're using the right fixture
        assert(CollectionPoint.objects.all().count() == 19)

        call_command('import_user', 'data/import_user_fixture.json', stdout=out)

        self.customer = Customer.objects.all().first()

    def test_active_customer_was_imported(self):

        # we should only have one customer here, and it should be joseph bloggs,
        # who we imported
        self.assertEqual("Joseph Bloggs", Customer.objects.all().first().full_name)

    def test_inactive_customer_was_not_imported(self):
        self.assertEqual(
            0,
            Customer.objects.filter(full_name="Francisco Rosa").count()
        )


    def test_imported_customer_has_collection_point(self):

        o_and_n = CollectionPoint.objects.get(name="Hackney City Farm")

        self.assertEqual(o_and_n.name, self.customer.collection_point.name)

    def test_imported_customer_has_bags(self):
        coc = CustomerOrderChange.objects.filter(customer=self.customer).first()
        cocbq = coc.bag_quantities.first()

        # should be "Large Veg"
        self.assertEqual("Large veg", cocbq.bag_type.name)
        self.assertEqual(1, cocbq.quantity)

    def test_imported_customer_uses_the_latest_active_mandate(self):
        # newer mandate in fixture was created on: "2016-05-23 13:48:37"
        # older mandate in fixture was created on: "2016-04-14 13:48:37"
        mandate = self.customer.gocardless_current_mandate

        self.assertEqual(mandate.created.year, 2016)
        self.assertEqual(mandate.created.month, 5)
        self.assertEqual(mandate.created.day, 23)
