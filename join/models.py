from billing_week import get_billing_week
from collections import OrderedDict
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone


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
    customer = models.ForeignKey(
        # Has to be a string because Customer is not defined yet.
        'Customer',
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
        related_name='go_cardless_mandate',
        null=True,
    )


class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
        related_name='customer'
    )
    # XXX ? created = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField()
    created_in_billing_week = models.CharField(max_length=9)
    full_name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=30)
    mobile = models.CharField(max_length=30, default='', blank=True)
    balance_carried_over = models.IntegerField(default=0)
    holiday_due = models.IntegerField(default=0)
    tags = models.ManyToManyField(CustomerTag, blank=True)
    gocardless_current_mandate = models.OneToOneField(
        BillingGoCardlessMandate,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
        related_name='in_use_for_customer',
        null=True,
    )

    def _get_latest_account_status(self):
        latest_account_status = AccountStatusChange.objects.order_by(
            '-changed'
        ).filter(customer=self)[:1][0]
        # Human readable?
        return latest_account_status.status
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
        ).filter(customer=self)[:1][0]
        return latest_cp.collection_point

    def _set_collection_point(self, collection_point_id):
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

    def _set_bag_quantities(self, bag_quantities):
        now = timezone.now()
        bw = get_billing_week(now)
        customer_order_change = CustomerOrderChange(
            changed=now,
            changed_in_billing_week=str(bw),
            customer=self,
        )
        customer_order_change.save()
        for bag_type_id, quantity in bag_quantities.items():
            bag_quantity = CustomerOrderChangeBagQuantity(
                customer_order_change=customer_order_change,
                bag_type_id=bag_type_id,
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
    leaving_date = models.DateTimeField(null=True)
    changed = models.DateTimeField()
    changed_in_billing_week = models.CharField(max_length=9)
    customer = models.ForeignKey(
        Customer,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
        related_name='account_status_change',
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
    changed = models.DateTimeField()
    changed_in_billing_week = models.CharField(max_length=9)
    customer = models.ForeignKey(
        Customer,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
    )

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


class BillingCredit(models.Model):
    customer = models.ForeignKey(
        Customer,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
        related_name='billing_credit',
    )
    created = models.DateTimeField(auto_now_add=True)
    # XXX What about when prices change and we've already got some skip
    # credits in place -> Prbably just add a manual credit to those accounts
    # where it is an issue.
    amount_pence = models.IntegerField()


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
            self.collection_date.isoformat(),
            self.created.isoformat(),
        )
