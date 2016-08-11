import csv

from django.core.management.base import BaseCommand, CommandError
from join.models import Customer, BagType
from join.helper import render_bag_quantities, calculate_weekly_fee


class Command(BaseCommand):
    help = 'Generated the Database Backup Example Report'

    def handle(self, *args, **options):
        header_row = ['first_name','surname','email','status','pickup','bags','on_holiday']
        for bag_type in BagType.objects.all():
            header_row.append(bag_type.name)
        writer = csv.writer(self.stdout)
        writer.writerow(header_row)
        for customer in Customer.objects.order_by('full_name'):
            bq = customer.bag_quantities
            row = [
                # first_name
                customer.full_name,
                # surname
                None,
                # email
                customer.user.email,
                # status
                customer.account_status,
                # pickup
                customer.collection_point,
                # bags
                render_bag_quantities(bq),
                # on_holiday
                customer.skipped,
            ]
            quantities = {}
            for bq in customer.bag_quantities:
                quantities[bq.bag_type] = bq.quantity
            for bag_type in BagType.objects.all():
                row.append(quantities.get(bag_type) and 1 or 0)
            writer.writerow(row)
        self.stderr.write(self.style.SUCCESS('Successfully generated report'))
