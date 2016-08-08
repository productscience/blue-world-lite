import csv

from django.core.management.base import BaseCommand, CommandError
from join.models import Customer
from join.helper import render_bag_quantities, calculate_weekly_fee


class Command(BaseCommand):
    help = 'Generated the Database Backup Example Report'

    def handle(self, *args, **options):
        self.stdout.write('first_name,surname,email,is_additional,status,address_1,address_2,address_3,postcode,email,telephone_1,telephone_2,mobile,additional_contact_info,pickup,discount,bags,fee,payment_method,so_details,so_day_of_month,start_date,stop_date,source,on_holiday\n')
        writer = csv.writer(self.stdout)
        for customer in Customer.objects.order_by('full_name'):
            bq = customer.bag_quantities
            row = [
                # first_name
                customer.full_name,
                # surname
                None,
                # email
                customer.user.email,
                # is_additional
                None,
                # status
                customer.account_status,
                # address_1,address_2,address_3,postcode,email,telephone_1,telephone_2,
                None,None,None,None,None,None,None,
                # mobile
                customer.mobile,
                # additional_contact_info,
                None,
                # pickup
                customer.collection_point,
                # discount
                None,
                # bags
                render_bag_quantities(bq),
                # fee (weekly now)
                calculate_weekly_fee(bq),
                # payment_method
                None,
                # so_details,so_day_of_month,
                None,None,
                # start_date,
                customer.created,
                # stop_date,source,
                None,None,
                # on_holiday
                customer.skipped
            ]
            writer.writerow(row)
        self.stderr.write(self.style.SUCCESS('Successfully generated report'))
