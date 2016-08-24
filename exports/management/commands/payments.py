import csv

from django.core.management.base import BaseCommand, CommandError
from exports.models import DataExport

class Command(BaseCommand):
    help = 'Generate payments report'

    def handle(self, *args, **options):
        header_row = DataExport.report_payments_header_row()
        writer = csv.writer(self.stdout)
        writer.writerow(header_row)
        for row in DataExport.report_payments():
            writer.writerow(row)
        self.stderr.write(self.style.SUCCESS('Successfully generated report'))
