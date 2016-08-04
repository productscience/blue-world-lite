import json

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from django.conf import settings

from join.models import AccountStatusChange
from join.models import Customer

from billing_week import get_billing_week

class Command(BaseCommand):
    """
    loads json at PATH provided, and creates
    - a user, with the same email, and name, and joined date
    - a customer, with the other
    - a set of bag choice changes for the user to represent their current bag choice

    usage: python manage.py import_user data/active.customers.and.bagchoices.json
    """


    help = ""

    def add_arguments(self, parser):
        parser.add_argument('path')

    def handle_noargs(self, **options):
        pass
        # now do the things that you want with your models here

    def _make_user(self, customer):
        """
        Creates a new user for the customer record passed in.
        Returns a newlt created user instance
        """

        username = "{}_{}".format(
            customer['fields'].get('first_name', '__').lower(),
            customer['pk'])
        if settings.FAKE_IMPORTED_EMAILS:
            email = "{}.{}@example.com".format(
                customer['fields'].get('first_name', '__').lower(),
                customer['fields'].get('surname', '__').lower())
        else:
            email = customer['fields'].get('email')
        password = "123123ab"


        user = User.objects.create_user(username, email, password)

        return user


    def _convert_bag_choices(self, old_bag_choices):
        chosen_bags = {}
        for obc in old_bag_choices:
            bag_type = obc['fields']['bag_type']
            bag_qty = obc['fields']['quantity']
            chosen_bags[bag_type] = bag_qty

        return chosen_bags

    def handle(self, *args, **options):
        json_path = options['path']

        self.stdout.write(self.style.NOTICE("looking up this path: {}".format(json_path)))
        with open(json_path) as data_file:
            blob_o_stuff = json.load(data_file)

            customers = [item for item in blob_o_stuff if item['model'] == 'customers.customer']
            bag_choices = [item for item in blob_o_stuff if item['model'] == 'customers.bagchoice']
            gc_subs = [item for item in blob_o_stuff if item['model'] == 'customers.gcsubscription']

            self.stdout.write(self.style.NOTICE("Found {} customer entries".format(len(customers))))
            self.stdout.write(self.style.NOTICE("Found {} bagchoice entries".format(len(bag_choices))))
            self.stdout.write(self.style.NOTICE("Found {} gc_sub entries".format(len(gc_subs))))

            total_customers = len(customers)
            for (index, c) in enumerate(customers):
                user = self._make_user(c)

                now = timezone.now()
                bw = get_billing_week(now)
                cf = c['fields']

                customer = Customer(
                    created=now,
                    created_in_billing_week=str(bw),
                    full_name="{} {}".format(cf['first_name'], cf['surname']),
                    nickname=cf['first_name'],
                    mobile=cf['telephone_1'],
                    user=user,
                    id=c['pk']
                )

                customer.save()

                account_status_change = AccountStatusChange(
                    changed=now,
                    changed_in_billing_week=str(bw),
                    customer=customer,
                    status=AccountStatusChange.ACTIVE,
                )
                account_status_change.save()

                old_bag_choices = [b
                                   for b in bag_choices
                                   if b['fields']['customer'] == c['pk']]

                customer.bag_quantities = self._convert_bag_choices(old_bag_choices)

                customer.collection_point = cf['pickup']
                self.stdout.write(self.style.SUCCESS("Imported {} of {}: {}".format(
                    index,
                    total_customers,
                    customer.full_name)))
                # TODO Make a corresponding BillingGoCardlessMandate
