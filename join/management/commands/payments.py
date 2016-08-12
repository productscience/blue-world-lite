import csv
import pytz

from django.core.management.base import BaseCommand, CommandError
from join.models import Payment, PaymentStatusChange
            

london = pytz.timezone("Europe/London")


class Command(BaseCommand):
    help = 'Generate payments report'

    def handle(self, *args, **options):
        header_row = ['customer', 'payment_id', 'created', 'completed', 'amount', 'status']
        writer = csv.writer(self.stdout)
        writer.writerow(header_row)
        payment_status_changes = (
            PaymentStatusChange.objects
            .order_by('payment', '-changed')
            .distinct('payment')
        )
        for psc in payment_status_changes:
            row = [
                psc.payment.customer,
                psc.payment.gocardless_payment_id,
                psc.payment.created and psc.payment.created.astimezone(london).strftime('%Y-%m-%d %H:%M'),
                psc.payment.completed and psc.payment.completed.astimezone(london).strftime('%Y-%m-%d %H:%M'),
                psc.payment.amount,
                psc.status
            ]
            writer.writerow(row)
        self.stderr.write(self.style.SUCCESS('Successfully generated report'))
