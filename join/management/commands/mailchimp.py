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
        for row in Customer.report_mailchimp():
            writer.writerow(row)
        self.stderr.write(self.style.SUCCESS('Successfully generated report'))
