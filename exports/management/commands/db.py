import csv
import pytz

from django.core.management.base import BaseCommand, CommandError
from export.models import DataExport

london = pytz.timezone("Europe/London")


class Command(BaseCommand):
    help = 'Generated the Database Backup Example Report'

    def handle(self, *args, **options):
        self.stdout.write('first_name,surname,email,is_additional,status,address_1,address_2,address_3,postcode,email,telephone_1,telephone_2,mobile,additional_contact_info,pickup,discount,bags,fee,payment_method,so_details,so_day_of_month,start_date,stop_date,source,on_holiday\n')
        writer = csv.writer(self.stdout)
        # this is a generator, yielding a row for each customer
        for row in DataExport.report_db():
            writer.writerow(row)
        self.stderr.write(self.style.SUCCESS('Successfully generated report'))
