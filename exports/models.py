import pytz

from django.db import models

from join.helper import calculate_weekly_fee
from join.models import BagType
from join.models import Customer, PaymentStatusChange
from join.models import AccountStatusChange
from join.helper import render_bag_quantities
from django.utils.html import format_html


london = pytz.timezone("Europe/London")

class DataExport(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=255)
    export_url = models.CharField(max_length=255)

    def export_link(self):
        return format_html("<a href='{}'>Download csv file</a>", self.export_url)

    def __str__(self):
        return self.title


    @classmethod
    def report_db_header_row(cls):
        return [
            'first_name',
            'surname',
            'email',
            'is_additional',
            'status',
            'address_1',
            'address_2',
            'address_3',
            'postcode',
            'email',
            'telephone_1',
            'telephone_2',
            'mobile',
            'additional_contact_info',
            'pickup',
            'discount',
            'bags',
            'fee',
            'payment_method',
            'so_details',
            'so_day_of_month',
            'start_date',
            'stop_date',
            'source',
            'on_holiday'
        ]

    @classmethod
    def report_db(cls):
        """
        generates a set of rows to be encoded for a CSV report
        """
        for customer in Customer.objects.order_by('full_name'):
            bq = customer.bag_quantities
            yield [
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
                None, None, None, None, None, None, None,
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
                None, None,
                # start_date,
                customer.created.astimezone(london).strftime('%Y-%m-%d %H:%M'),
                # stop_date,source,
                None, None,
                # on_holiday
                customer.skipped
            ]

    @classmethod
    def report_mailchimp_header_row(cls):
        """
        Returns header for for mailchimp export
        """
        header_row = [
            'first_name',
            'surname',
            'email',
            'status',
            'pickup',
            'bags',
            'on_holiday'
        ]
        for bag_type in BagType.objects.all():
            header_row.append(bag_type.name)

        return header_row

    @classmethod
    def report_mailchimp(cls):
        """
        generates a set of rows for mailchimp export
        """
        for customer in Customer.objects.order_by('full_name'):
            bq = customer.bag_quantities
            row = [
                # first_name
                customer.full_name,
                # surname
                None,
                # email
                customer.user.email,
                # status
                customer.account_status,
                # pickup
                customer.collection_point,
                # bags
                render_bag_quantities(bq),
                # on_holiday
                customer.skipped,
            ]
            quantities = {}
            for bq in customer.bag_quantities:
                quantities[bq.bag_type] = bq.quantity
            for bag_type in BagType.objects.all():
                row.append(quantities.get(bag_type) and 1 or 0)

            yield row

    @classmethod
    def report_churn_header_row(cls):
        """
        Generates the header for a CSV export
        """
        return ['customer', 'changed', 'status']

    @classmethod
    def report_churn(cls):
        """
        generates a set of rows for CSV export
        """
        for account_status_change in AccountStatusChange.objects.all():
            yield [
                account_status_change.customer.full_name,
                account_status_change.changed.astimezone(london).strftime('%Y-%m-%d %H:%M'),
                account_status_change.status,
            ]


    @classmethod
    def report_payments_header_row(cls):
        return [
            'customer',
            'payment_id',
            'created',
            'completed',
            'amount',
            'status'
        ]

    @classmethod
    def report_payments(cls):
        """
        Generate rows for payments report CSV
        """
        payment_status_changes = (
            PaymentStatusChange.objects
            .order_by('payment', '-changed')
            .distinct('payment')
        )
        for psc in payment_status_changes:
            yield [
                psc.payment.customer,
                psc.payment.gocardless_payment_id,
                psc.payment.created and psc.payment.created.astimezone(london).strftime('%Y-%m-%d %H:%M'),
                psc.payment.completed and psc.payment.completed.astimezone(london).strftime('%Y-%m-%d %H:%M'),
                psc.payment.amount,
                psc.status
            ]
