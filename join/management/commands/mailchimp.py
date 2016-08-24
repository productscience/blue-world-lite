import csv

from django.core.management.base import BaseCommand, CommandError
from exports.models import DataExport

class Command(BaseCommand):
    help = 'Generated the Database Backup Example Report'

    def handle(self, *args, **options):
        writer = csv.writer(self.stdout)
        header_row = DataExport.report_mailchimp_header_row()
        writer.writerow(header_row)
        for row in DataExport.report_mailchimp():
            writer.writerow(row)
        self.stderr.write(self.style.SUCCESS('Successfully generated report'))
