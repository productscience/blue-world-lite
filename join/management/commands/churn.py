import csv
import pytz

from django.core.management.base import BaseCommand, CommandError
from join.models import AccountStatusChange
            

london = pytz.timezone("Europe/London")


class Command(BaseCommand):
    help = 'Generate payments report'

    def handle(self, *args, **options):
        header_row = ['customer', 'changed', 'status']
        writer = csv.writer(self.stdout)
        writer.writerow(header_row)
        for account_status_change in AccountStatusChange.objects.all():
            row = [
                account_status_change.customer.full_name,
                account_status_change.changed.astimezone(london).strftime('%Y-%m-%d %H:%M'),
                account_status_change.status,
            ]
            writer.writerow(row)
        self.stderr.write(self.style.SUCCESS('Successfully generated report'))
