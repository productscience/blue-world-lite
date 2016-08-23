import csv
import pytz

from django.core.management.base import BaseCommand, CommandError
from join.models import AccountStatusChange


london = pytz.timezone("Europe/London")


class Command(BaseCommand):
    help = 'Generate payments report'

    def handle(self, *args, **options):

        writer = csv.writer(self.stdout)
        writer.writerow(AccountStatusChange.report_churn_header_row())
        for row in AccountStatusChange.report_churn():
            writer.writerow(row)
        self.stderr.write(self.style.SUCCESS('Successfully generated report'))
