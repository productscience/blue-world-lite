import csv
import pytz

from django.core.management.base import BaseCommand, CommandError
from join.models import Payment, PaymentStatusChange


london = pytz.timezone("Europe/London")


class Command(BaseCommand):
    help = 'Generate payments report'

    def handle(self, *args, **options):
        header_row = PaymentStatusChange.report_payments_header_row()
        writer = csv.writer(self.stdout)
        writer.writerow(header_row)
        for row in PaymentStatusChange.report_payments():
            writer.writerow(row)
        self.stderr.write(self.style.SUCCESS('Successfully generated report'))
