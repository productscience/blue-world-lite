import csv

from django.core.management.base import BaseCommand, CommandError
from join.models import Customer, BagType
from join.helper import render_bag_quantities, calculate_weekly_fee


class Command(BaseCommand):
    help = 'Generated the Database Backup Example Report'

    def handle(self, *args, **options):
        writer = csv.writer(self.stdout)
        header_row = Customer.report_mailchimp_header_row()
        writer.writerow(header_row)
        for row in Customer.report_mailchimp():
            writer.writerow(row)
        self.stderr.write(self.style.SUCCESS('Successfully generated report'))
