from django.utils.six import StringIO
from django.test import TransactionTestCase
from django.core.management import call_command

from .models import BillingGoCardlessMandate, CollectionPoint, Customer

class ImportUserWithManagementTestCase(TransactionTestCase):
    """
    Tests that a customer who has been imported is Class-based
    as an active user, with a working mandate/pre-auth for taking
    payments
    """

    # set up using special import user fixture just for this one
    fixtures = ['data/user.json', 'initial.json']


    def test_command_output(self):
        #  call management command
        out = StringIO()

        # check we've imported all our collection points
        # we'll need for the import

        assert(CollectionPoint.objects.all().count() == 19)

        call_command('import_user', 'data/import_user_fixture.json', stdout=out)

        # assert we have a user with a:
            # collection point
            # active mandate in use, which
            # regular order
        self.assertEqual(BillingGoCardlessMandate.objects.all().count(), 1)

        #  then check should be included in a packing list
