from billing_week import get_billing_week
from collections import OrderedDict
from decimal import Decimal
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from billing_week import get_billing_week, parse_billing_week
from django.utils import timezone
from join.helper import calculate_weekly_fee


class CollectionPoint(models.Model):
    name = models.CharField(
        max_length=40,
        help_text="e.g. 'The Old Fire Station'",
        null=False,
        unique=True,
    )
    location = models.CharField(
        null=True,
        blank=True,
        max_length=100,
        help_text="E.g. 'Leswin Road, N16'"
    )
    latitude = models.FloatField(
        null=True,
        blank=True,
        help_text='''
        Allows your pickup to show on a map. Latitude should be
        between 49 and 60 in the UK. You can find latitude and longitude by
        following these instructions: <ol><li>Go to <a
        href='http://maps.google.co.uk/' target='_NEW'>Google
        maps</a></li><li>Click the tiny green flask icon on the
        top-right</li><li>Scroll down and enable the 'LatLng Tool
        Tip'</li><li>Find your pickup and zoom in close</li><li>You'll see
        (latitude, longitude) showing on the mouse pointer</li><li>Note them
        down and copy latitude into the field above and longitude into the
        field below</li></ol>
        '''
    )
    longitude = models.FloatField(
        null=True,
        blank=True,
        help_text='Longitude should be between -10 and 2 in the UK'
    )
    active = models.BooleanField(
        default=True,
        help_text='''
        You can mark this pickup as not available if you need to. This might
        be because it is full for example.
        '''
    )
    FULL = 'FULL'
    CLOSING_DOWN = 'CLOSING_DOWN'
    INACTIVE_REASON_CHOICES = (
        (FULL, 'Full'),
        (CLOSING_DOWN, 'Closing down'),
    )
    inactive_reason = models.CharField(
        max_length=255,
        choices=INACTIVE_REASON_CHOICES,
        default=FULL,
        null=True
    )
    WED_THURS = 'WED_THURS'
    WED = 'WED'
    THURS = 'THURS'
    COLLECTION_DAY_CHOICES = (
        (WED_THURS, 'Wednesday and Thursday'),
        (WED, 'Wednesday'),
        (THURS, 'Thursday'),
    )
    collection_day = models.CharField(
        max_length=255,
        choices=COLLECTION_DAY_CHOICES,
        default=WED,
    )
    display_order = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-active', 'display_order']


class BagType(models.Model):
    name = models.CharField(
        max_length=50,
        help_text="E.g. 'Standard veg'.",
        null=False,
        unique=True,
    )
    tag_color = models.CharField(
        max_length=50,
        help_text="String used on the packing list for the bag colour",
        null=True,
        default='',
        blank=True,
    )
    display_order = models.IntegerField(
        null=True,
        blank=True,
        help_text='''
        Bags will be sorted by this number.
        '''
    )
    active = models.BooleanField(
        default=True,
        help_text='Active bags appear in the joining form.'
    )

    def _set_weekly_cost(self, weekly_cost):
        assert isinstance(weekly_cost, Decimal), \
            'Expecting a decimal, not {!r}'.format(weekly_cost)
        # XXX Potential race condition here
        cost_changes = BagTypeCostChange.objects.order_by(
            '-changed'
        ).filter(bag_type=self)[:1]
        if not len(cost_changes) or cost_changes[0].weekly_cost != weekly_cost:
            now = timezone.now()
            bw = get_billing_week(now)
            cost_change = BagTypeCostChange(
                changed=now,
                changed_in_billing_week=str(bw),
                weekly_cost=weekly_cost,
                bag_type=self
            )
            cost_change.save()

    def _get_weekly_cost(self):
        'Returns the latest weekly cost'
        latest_cost_change = BagTypeCostChange.objects.order_by(
            '-changed'
        ).filter(bag_type=self)[:1][0]
        return latest_cost_change.weekly_cost
    weekly_cost = property(_get_weekly_cost, _set_weekly_cost)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['display_order']


# XXX Cost should surely be price?
class BagTypeCostChange(models.Model):
    changed = models.DateTimeField()
    changed_in_billing_week = models.CharField(max_length=9)
    bag_type = models.ForeignKey(
        BagType,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
        related_name='cost_changes'
    )
    weekly_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Enter the weekly fee for receiving this bag.',
        verbose_name='Weekly cost',
    )

    def __str__(self):
        return '{} {} {}'.format(
            self.bag_type.name,
            self.changed.strftime('%Y-%m-%d'),
        )


class CustomerTag(models.Model):
    tag = models.CharField(max_length=255)

    def __str__(self):
        return self.tag

    class Meta:
        ordering = ('tag',)


class BillingGoCardlessMandate(models.Model):
    session_token = models.CharField(max_length=255, default='')
    gocardless_redirect_flow_id = models.CharField(max_length=255, default='')
    gocardless_mandate_id = models.CharField(max_length=255, default='')
    created = models.DateTimeField()
    created_in_billing_week = models.CharField(max_length=9)
    completed = models.DateTimeField(null=True, blank=True)
    completed_in_billing_week = models.CharField(max_length=9, null=True, blank=True)
    amount_notified = models.DecimalField(max_digits=6, decimal_places=2)
    customer = models.ForeignKey(
        # Has to be a string because Customer is not defined yet.
        'Customer',
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
        related_name='go_cardless_mandate',
        null=True,
    )



class CustomerManager(models.Manager):
    def create_now(self, **p):
        assert 'created' not in p
        assert 'created_in_billing_week' not in p
        if 'now' not in p:
            p['now'] = timezone.now()
        now = p['now']
        del p['now']
        p['created'] = now
        p['created_in_billing_week'] = str(get_billing_week(now))
        return self.create(**p)


class Customer(models.Model):

    def save(self, *args, **kwargs):
        if not self.full_name:
            raise ValidationError('The full_name field is required')
        super(Customer, self).save(*args, **kwargs)

    objects = CustomerManager()

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
        related_name='customer',
        null=True
    )
    # XXX ? created = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField()
    created_in_billing_week = models.CharField(max_length=9)
    full_name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=30)
    mobile = models.CharField(max_length=30, default='', blank=True)
    balance_carried_over = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal(0.00),
    )
    holiday_due = models.IntegerField(default=0)
    tags = models.ManyToManyField(CustomerTag, blank=True)
    gocardless_current_mandate = models.OneToOneField(
        BillingGoCardlessMandate,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
        related_name='in_use_for_customer',
        null=True,
    )

    def account_status_before(self, d=None):
        if d:
            status = AccountStatusChange.objects.order_by(
                '-changed'
            ).filter(customer=self, changed__lt=d)[:1][0]
        else:
            status = AccountStatusChange.objects.order_by(
                '-changed'
            )[:1][0]
        return status.status

    def _get_latest_account_status(self):
        return self.account_status_before()
    account_status = property(_get_latest_account_status)



    def _has_left(self):
        return self.account_status == AccountStatusChange.LEFT
    has_left = property(_has_left)

    # def _is_leaving(self):
    #     return self.account_status == AccountStatusChange.LEAVING
    # is_leaving = property(_is_leaving)

    def _get_latest_collection_point(self):
        latest_cp = CustomerCollectionPointChange.objects.order_by(
            '-changed'
        ).filter(customer=self)[:1]
        if not latest_cp:
            raise ValueError('No collection point for customer: {}'.format(self))
        return latest_cp[0].collection_point

    def _set_collection_point(self, collection_point_id):
        if not isinstance(collection_point_id, int):
            collection_point_id = collection_point_id.id
        now = timezone.now()
        bw = get_billing_week(now)
        collection_point_change = CustomerCollectionPointChange(
            changed=now,
            changed_in_billing_week=str(bw),
            customer=self,
            collection_point_id=collection_point_id,
        )
        collection_point_change.save()
    collection_point = property(
        _get_latest_collection_point,
        _set_collection_point,
    )

    def _get_latest_bag_quantities(self):
        latest_order = CustomerOrderChange.objects.order_by(
            '-changed'
        ).filter(customer=self)[:1][0]
        return latest_order.bag_quantities.all()

    def _set_bag_quantities(self, bag_quantities, reason='CHANGE'):
        now = timezone.now()
        bw = get_billing_week(now)
        customer_order_change = CustomerOrderChange(
            changed=now,
            changed_in_billing_week=str(bw),
            customer=self,
            reason=reason,
        )
        customer_order_change.save()
        for bag_type, quantity in bag_quantities.items():
            if not isinstance(bag_type, BagType):
                bag_quantity = CustomerOrderChangeBagQuantity(
                    customer_order_change=customer_order_change,
                    bag_type_id=int(bag_type),
                    quantity=quantity,
                )
            else:
                bag_quantity = CustomerOrderChangeBagQuantity(
                    customer_order_change=customer_order_change,
                    bag_type=bag_type,
                    quantity=quantity,
                )
            # XXX Do we need the save?
            bag_quantity.save()

    bag_quantities = property(_get_latest_bag_quantities, _set_bag_quantities)

    def _get_skipped(self):
        skipped_dates = []
        now = timezone.now()
        bw = get_billing_week(now)
        bwstr = str(bw)
        if Skip.objects.filter(customer=self, billing_week=str(bwstr)).all():
            return True
        return False

    skipped = property(_get_skipped)

    def __str__(self):
        return '{} ({})'.format(self.full_name, self.nickname)


class AccountStatusChange(models.Model):
    AWAITING_DIRECT_DEBIT = 'AWAITING_DIRECT_DEBIT'
    ACTIVE = 'ACTIVE'
    LEFT = 'LEFT'
    STATUS_CHOICES = (
        (AWAITING_DIRECT_DEBIT, 'Awating Go Cardless'),
        (ACTIVE, 'Active'),
        (LEFT, 'Left'),
    )
    # leaving_date = models.DateTimeField(null=True)
    changed = models.DateTimeField()
    changed_in_billing_week = models.CharField(max_length=9)
    customer = models.ForeignKey(
        Customer,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
        related_name='account_status_changes',
    )
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)

    def __str__(self):
        return 'Account Status Change for {} on {}'.format(
            self.customer.full_name,
            self.changed.strftime('%Y-%m-%d'),
        )


class CustomerCollectionPointChange(models.Model):
    changed = models.DateTimeField()
    changed_in_billing_week = models.CharField(max_length=9)
    customer = models.ForeignKey(
        Customer,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
    )
    collection_point = models.ForeignKey(
        CollectionPoint,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return '{} -> {} on {}'.format(
            self.customer.full_name,
            self.collection_point.name,
            self.changed.isoformat(),
        )


class CustomerOrderChange(models.Model):
    @classmethod
    def as_of(cls, billing_week, customer=None):
        order_changes = (
            CustomerOrderChange.objects
            .filter(changed_in_billing_week__lt=str(billing_week))
            .order_by('customer', '-changed')
            .distinct('customer')
            .only('id')
        )
        if customer is not None:
            order_changes = order_changes.filter(customer=customer)
        return (
            CustomerOrderChangeBagQuantity.objects
            .filter(customer_order_change__in=order_changes)
            .order_by('customer_order_change__customer__full_name')
            .only('customer_order_change__customer_id', 'bag_type_id', 'quantity')
        )

    changed = models.DateTimeField()
    changed_in_billing_week = models.CharField(max_length=9)
    customer = models.ForeignKey(
        Customer,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
    )
    JOIN = 'JOIN'
    CHANGE = 'CHANGE'
    REASON_CHOICES = (
        (JOIN, 'Join'),
        (CHANGE, 'Change'),
    )
    reason = models.CharField(max_length=255, choices=REASON_CHOICES, default=CHANGE)

    def __str__(self):
        return 'Customer Order Change for {} on {}'.format(
            self.customer.full_name,
            self.changed.strftime('%Y-%m-%d'),
        )


class CustomerOrderChangeBagQuantity(models.Model):
    customer_order_change = models.ForeignKey(
        CustomerOrderChange,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
        related_name='bag_quantities',
    )
    bag_type = models.ForeignKey(
        BagType,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
    )
    quantity = models.IntegerField()

    class Meta:
        verbose_name_plural = 'customer order changes bag quantities'

    def __str__(self):
        return (
            'Customer Order Change Bag Quantity for {} chose {} {} at {}'
        ).format(
            self.customer_order_change.customer.full_name,
            self.quantity,
            self.bag_type.name,
            self.customer_order_change.changed.strftime('%Y-%m-%d'),
        )


class Skip(models.Model):
    billing_week = models.CharField(max_length=9)
    created = models.DateTimeField(auto_now_add=True)
    created_in_billing_week = models.CharField(max_length=9)
    customer = models.ForeignKey(
        Customer,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
        related_name='skip',
    )

    def __str__(self):
        return '{} skiped week {} on {}'.format(
            self.customer.full_name,
            self.billing_week,
            self.created.isoformat(),
        )

class Reminder(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    )
    title = models.CharField(max_length=30)
    date = models.DateField(null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    done = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title

    def __str__(self):
        return "{} - {}".format(self.date, self.title)

    class Meta:
        ordering = ['-date']

    def is_due(self):
        return self.date <= timezone.now()
        # return self.date <= datetime.date.today()


class Payment(models.Model):
    @classmethod
    def create_payments(cls, year, month, start_customer=0):
        now = timezone.now()

        # If the account is in credit after taking the line items into account, it will be ignored this month.
        # Upcoming line items can show on the billing history page.
        now_bw = get_billing_week(now)
        # Find the last deadline of the month
        billing_week = parse_billing_week('{0}-{1:02d} {2}'.format(year, month, 1))
        assert now_bw >= billing_week, 'Cannot create payments in the future'

        last_run = PaymentRun.objects.order_by('-started')[:1]
        if last_run:
            assert last_run[0].started < now, 'The last run was in the future'

        payment_run = PaymentRun.objects.create(
            job_id = 'xxx',
            year = year,
            month = month,
            started = now,
            finished =None,
            start_customer = start_customer or None,
            currently_processing_customer = None,
        )
        payment_run.save()
        payment_by_customer = {}
        # For each customer
        for customer in Customer.objects.order_by('pk'):
            if customer.pk < start_customer:
                print('Skip')
                continue
            if not payment_run.start_customer:
                payment_run.start_customer = customer
            payment_run.currently_processing_customer = customer
            payment_run.save()
            print(customer)
            # Look at *all* line items that don't have a payment and create the payment object for them
            line_items = LineItem.objects.filter(payment=None, customer=customer)
            total = Decimal(0)
            for line_item in line_items:
                total += line_item.amount
            print(total)
            # If the account is in credit after taking the line items into account, it will be ignored this month.
            if total > 0:
                if not settings.SKIP_GOCARDLESS:
                    mandate_id = payment.customer.gocardless_current_mandate.gocardless_mandate_id
                    payment_response_id, payment_response_status = payment.send_to_gocardless(mandate_id, payment.amount)
                else:
                    mandate_id = 'none'
                    payment_response_id = 'none'
                    payment_response_status = 'skipped'
                payment = Payment(
                    customer=customer,
                    gocardless_mandate_id=mandate_id,
                    amount=total,
                    reason=Payment.MONTHLY_INVOICE,
                    gocardless_payment_id=payment_response_id,
                    created=now,
                    created_in_billing_week=str(now_bw),
                )
                payment.save()
                payment_status_change = PaymentStatusChange(
                    changed=now,
                    changed_in_billing_week=str(now_bw),
                    status=payment_response_status,
                    payment=payment,
                )
                payment_status_change.save()
                for line_item in line_items:
                    line_item.payment = payment
                    line_item.save()
                payment_by_customer[customer] = payment
        return payment_by_customer


    @classmethod
    def send_to_gocardless(cls, mandate_id, amount_pounds):
        assert amount_pounds < 1000, 'Unusual to have a £1000 bill'
        mr = settings.GOCARDLESS_CLIENT.mandates.get(mandate_id)
        next_possible_charge_date = mr.next_possible_charge_date
        params = {
            "amount": int(amount_pounds * 100), # This is in pence
            "currency": "GBP",
            # If not specified means ASAP.
            "charge_date": next_possible_charge_date, #now.date().isoformat(), #datetime.date.now().strftime('%Y-%m-%d'),
            # "reference": "GROCOM",
            "metadata": {
              # Shows on the payments page for GoCardless
              # "reconcile_end_month": "2016-01",
            },
            "links": {
              "mandate": mandate_id,
            },
        }
        payment_response = settings.GOCARDLESS_CLIENT.payments.create(params=params)
        print(payment_response.attributes)
#         # .attrubtes: {'reference': None, 'links': {'mandate': 'MD0000VWFBW3HR', 'creditor': 'CR000049T7G1D4'}, 'metadata': {'reconcile_end_month': '2016-01'}, 'amount_refunded': 0, 'status': 'pending_submission', 'amount': 100, 'id': 'PM0001J8NVC4R4', 'currency': 'GBP', 'charge_date': '2016-07-26', 'created_at': '2016-07-20T11:55:07.407Z', 'description': None}
        payment_response_id = payment_response.id
        payment_response_status = payment_response.status
        return payment_response_id, payment_response_status


    customer = models.ForeignKey(
        Customer,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
        related_name='payments',
    )
    description = models.CharField(max_length=1000)
    created = models.DateTimeField()
    created_in_billing_week = models.CharField(max_length=9)
    completed = models.DateTimeField(null=True, blank=True)
    completed_in_billing_week = models.CharField(max_length=9, null=True, blank=True)
    gocardless_mandate_id = models.CharField(max_length=255)
    amount = models.DecimalField(
        max_digits=12,  # XXX Could use something smaller
        decimal_places=2,
        null=False,
        blank=False,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    gocardless_payment_id = models.CharField(max_length=255)


    def _get_latest_status(self):
        return self.status_changes.order_by('-changed')[0].status
    status = property(_get_latest_status)


    JOIN_WITH_COLLECTIONS_AVAILABLE = 'JOIN_WITH_COLLECTIONS_AVAILABLE'
    MONTHLY_INVOICE = 'MONTHLY_INVOICE'
    MANUAL = 'MANUAL'
    REASON_CHOICES = (
        (JOIN_WITH_COLLECTIONS_AVAILABLE, 'Joined with collections available in the current month'),
        (MONTHLY_INVOICE, "Regular monthly invoice for next month's bags"),
        (MANUAL, 'Adjustment applied by Growing Communities staff'),
    )
    reason = models.CharField(max_length=255, choices=REASON_CHOICES)

    def __str__(self):
        return 'Payment of {} for {} on {}, billing week {}'.format(
            self.amount,
            self.customer.full_name,
            self.created.strftime('%Y-%m-%d %H:%M'),
            self.created_in_billing_week,
        )


class LineItemRun(models.Model):
    job_id = models.CharField(max_length=255)
    year = models.IntegerField()
    month = models.IntegerField()
    started = models.DateTimeField()
    finished = models.DateTimeField(blank=True, null=True)
    start_customer = models.ForeignKey(
        # Has to be a string because Customer is not defined yet.
        'Customer',
        # XXX Not sure about this yet
        related_name='line_item_run_starts',
        on_delete=models.CASCADE,
        null=True,
    )
    # In case we crash and need to restart
    currently_processing_customer = models.ForeignKey(
        # Has to be a string because Customer is not defined yet.
        'Customer',
        # XXX Not sure about this yet
        related_name='line_item_run_currents',
        on_delete=models.CASCADE,
        null=True,
    )


class PaymentRun(models.Model):
    job_id = models.CharField(max_length=255)
    year = models.IntegerField()
    month = models.IntegerField()
    started = models.DateTimeField()
    finished = models.DateTimeField(blank=True, null=True)
    start_customer = models.ForeignKey(
        # Has to be a string because Customer is not defined yet.
        'Customer',
        # XXX Not sure about this yet
        related_name='payment_run_starts',
        on_delete=models.CASCADE,
        null=True,
    )
    currently_processing_customer = models.ForeignKey(
        # Has to be a string because Customer is not defined yet.
        'Customer',
        # XXX Not sure about this yet
        related_name='payment_run_currents',
        on_delete=models.CASCADE,
        null=True,
    )


class LineItem(models.Model):

    @classmethod
    def create_line_items(cls, year, month, start_customer=0):
        '''
        We run this immediately after the billing date affecting the first billing
        week of the month.  So, if given 2016, 8 to run a bill in advance for
        August, the code should be run on Sunday 31 July 2016 just after 3pm GMT.

        We will create line items for August, and adjustments due during July.


        XXX What happens if someone leaves - should we automatically set skip weeks
            until the end of the month -> Then Leave status only applies on the month
            following and skip weeks is what causes the refund

        XXX Also need to make sure that collection points don't show up for LEAVEs
        '''
        # e.g. 31st July 2016
        now = timezone.now()

        last_run = LineItemRun.objects.order_by('-started')[:1]
        if last_run:
            assert last_run[0].started < now, 'The last run was in the future'

        line_item_run = LineItemRun.objects.create(
            job_id = 'xxx',
            year = year,
            month = month,
            started = now,
            finished =None,
            start_customer = start_customer or None,
            currently_processing_customer = None,
        )
        line_item_run.save()
        line_items_by_customer = {}
        now_bw = get_billing_week(now)
        # Find the last first billing week of the previous month
        billing_week = future_billing_week = parse_billing_week('{0}-{1:02d} {2}'.format(year, month, 1))
        assert now_bw >= billing_week, 'Cannot run line items for future weeks'
        billing_weeks_next_month = []
        while future_billing_week.month == month:
            billing_weeks_next_month.append(future_billing_week)
            future_billing_week = future_billing_week.next()

        old_billing_week = start = billing_week.prev()
        billing_weeks_last_month = []
        while old_billing_week.month == start.month:
            billing_weeks_last_month.append(old_billing_week)
            old_billing_week = old_billing_week.prev()
        billing_weeks_last_month.reverse()

        print(billing_weeks_last_month)
        print(billing_weeks_next_month)

        # For each customer
        customers = Customer.objects.order_by('pk').filter(created__lt=billing_weeks_next_month[0].start)
        print(customers.all())
        for customer in customers:
            if customer.pk < start_customer:
                continue
            if not line_item_run.start_customer:
                line_item_run.start_customer = customer
            line_item_run.currently_processing_customer = customer
            line_item_run.save()
            print('Processing', customer, customer.account_status_before(billing_weeks_next_month[0].start))

            if customer.account_status_before(billing_weeks_next_month[0].start) not in (AccountStatusChange.AWAITING_DIRECT_DEBIT,):
                # For each billing week in the previous month...
                for past_billing_week in billing_weeks_last_month:
                    # Look up what the order actually was
                    bag_quantities = CustomerOrderChange.as_of(past_billing_week, customer=customer)
                    should_have_billed = calculate_weekly_fee(bag_quantities)
                    # Look up the line item for that week
                    lis = LineItem.objects.filter(
                        customer=customer,
                        bill_against=str(past_billing_week),
                        reason__in=(LineItem.REGULAR, LineItem.NEW_JOINER),
                    ).all()
                    assert len(lis) <= 1
                    if len(lis) == 1:
                        billed = lis[0].amount
                    else:
                        billed = 0
                    print('Billed:', billed, 'Should have billed:', should_have_billed)
                    correction = should_have_billed - billed
                    if correction != 0:
                        cli = LineItem(
                            amount=correction,
                            created=now,
                            created_in_billing_week=now_bw,
                            customer=customer,
                            bill_against=str(past_billing_week),
                            reason=LineItem.ORDER_CHANGE_ADJUSTMENT,
                        )
                        cli.save()
                        line_items_by_customer.setdefault(customer, []).append(cli)
                    # If there is a skip week, refund the cost of the new order
                    skips = Skip.objects.filter(customer=customer, billing_week=past_billing_week).all()
                    assert len(skips) <= 1
                    if len(skips):
                        print('Skips:', skips, past_billing_week, -should_have_billed)
                        cli = LineItem(
                            amount=-should_have_billed,
                            created=now,
                            created_in_billing_week=now_bw,
                            customer=customer,
                            bill_against=str(past_billing_week),
                            reason=LineItem.SKIP_REFUND,
                        )
                        cli.save()
                        line_items_by_customer.setdefault(customer, []).append(cli)
            # If the customer has left, or not set up don't bill them:
            if customer.account_status_before(billing_weeks_next_month[0].start) not in (AccountStatusChange.AWAITING_DIRECT_DEBIT, AccountStatusChange.LEFT):
                # For each billing week in the next month, add a line item to the order
                print('Adding in line items for next months order')
                next_month_bag_quantities = CustomerOrderChange.as_of(
                    billing_weeks_next_month[0],
                    customer=customer,
                )
                weekly_cost = calculate_weekly_fee(next_month_bag_quantities)
                for future_billing_week in billing_weeks_next_month:
                    li = LineItem(
                        amount=weekly_cost,
                        created=now,
                        created_in_billing_week=now_bw,
                        customer=customer,
                        bill_against=str(future_billing_week),
                        reason=LineItem.REGULAR,
                    )
                    li.save()
                    line_items_by_customer.setdefault(customer, []).append(li)
        return line_items_by_customer

    created = models.DateTimeField()
    created_in_billing_week = models.CharField(max_length=9)
    description = models.CharField(max_length=1000)
    bill_against = models.CharField(max_length=9)
    payment = models.ForeignKey(
        Payment,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
        related_name='line_items',
        null=True,
    )
    customer = models.ForeignKey(
        # Has to be a string because Customer is not defined yet.
        'Customer',
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
        related_name='line_items',
        null=True,
    )
    amount=models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=False,
        blank=False,
    )
    NEW_JOINER = 'NEW_JOINER'
    MANUAL = 'MANUAL'
    REGULAR = 'REGULAR_ORDER_FOR_WEEK'
    SKIP_REFUND = 'SKIP_REFUND'
    ORDER_CHANGE_ADJUSTMENT = 'ORDER_CHANGE_ADJUSTMENT'
    REASON_CHOICES = (
        (MANUAL, 'Adjustment applied by Growing Communities Staff'),
        (NEW_JOINER, 'New Joiner'),
        (REGULAR, 'Regular weekly order charge'),
        (SKIP_REFUND, 'Refund from skipped week'),
        (ORDER_CHANGE_ADJUSTMENT, 'Adjustment from a changed order'),
    )
    reason = models.CharField(max_length=255, choices=REASON_CHOICES)

    def __str__(self):
        return 'LineItem {} {} for {} in {}'.format(
            self.reason,
            self.customer.full_name,
            self.amount,
            self.bill_against,
        )


class PaymentStatusChange(models.Model):
    changed = models.DateTimeField()
    changed_in_billing_week = models.CharField(max_length=9)
    payment = models.ForeignKey(
        Payment,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
        related_name='status_changes',
    )
    status = models.CharField(max_length=255)

    def __str__(self):
        return 'Payment Status Change to {} for {} on {}'.format(
            self.status,
            self.payment.customer.full_name,
            self.changed.strftime('%Y-%m-%d'),
        )


class GoCardlessEvent(models.Model):
    event_id =  models.CharField(max_length=100)
    event = JSONField()
