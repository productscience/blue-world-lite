from django.db import models
from django.conf import settings


class CollectionPoint(models.Model):
    name = models.CharField(max_length=40, help_text="e.g. 'The Old Fire Station'", null=False, unique=True)
    location = models.CharField(null=True, blank=True, max_length=100, help_text="E.g. 'Leswin Road, N16'")
    latitude = models.FloatField(null=True, blank=True, help_text="Allows your pickup to show on a map. Latitude should be between 49 and 60 in the UK. You can find latitude and longitude by following these instructions: <ol><li>Go to <a href='http://maps.google.co.uk/' target='_NEW'>Google maps</a></li><li>Click the tiny green flask icon on the top-right</li><li>Scroll down and enable the 'LatLng Tool Tip'</li><li>Find your pickup and zoom in close</li><li>You'll see (latitude, longitude) showing on the mouse pointer</li><li>Note them down and copy latitude into the field above and longitude into the field below</li></ol>")
    longitude = models.FloatField(null=True, blank=True, help_text="Longitude should be between -10 and 2 in the UK")
    active = models.BooleanField(default=True, help_text="You can mark this pickup as not available if you need to. This might be because it is full for example.")
    display_order = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-active', 'display_order']


class BagType(models.Model):
    """Each group has some bag types defined so that their customers can select them from the joining form"""
    name = models.CharField(max_length=50, help_text="E.g. 'Standard veg'.", null=False, unique=True)


    def _get_weekly_cost(self):
        "Returns the latest weekly cost"
        latest_bag_type_cost_change = BagTypeCostChange.objects.order_by('-changed').filter(bag_type=self)[:1][0]
        return latest_bag_type_cost_change.weekly_cost
    weekly_cost = property(_get_weekly_cost)


    display_order = models.IntegerField(null=True, blank=True, help_text="Bags will be sorted by this number (though they will always be grouped into fruit or veg first)")
    active = models.BooleanField(default=True, help_text="Active bags appear in the joining form.")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['display_order']


# XXX Cost should surely be price?
class BagTypeCostChange(models.Model):
    changed = models.DateTimeField(auto_now_add=True)
    bag_type = models.ForeignKey(
        BagType,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
    )
    weekly_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Enter the weekly fee for receiving this bag.",
        verbose_name="Weekly cost",
    )

    def __str__(self):
        return '{} {} {}'.format(self.bag_type.name, self.changed.strftime('%Y-%m-%d'))


class CustomerTag(models.Model):
    tag = models.CharField(max_length=255)

    def __str__(self):
        return self.tag

    class Meta:
        ordering = ('tag',)


class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
    )
    full_name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=30)
    mobile = models.CharField(max_length=30)
    go_cardless = models.CharField(max_length=30, default='')

    tags = models.ManyToManyField(CustomerTag)

    def _get_latest_account_status(self):
        latest_account_status = AccountStatusChange.objects.order_by('-changed').filter(customer=self)[:1][0]
        return latest_account_status.status
    account_status = property(_get_latest_account_status)

    def _has_left(self):
        return self.account_status == AccountStatusChange.LEFT
    has_left = property(_has_left)

    def _get_latest_collection_point(self):
        latest_collection_point = CustomerCollectionPointChange.objects.order_by('-changed').filter(customer=self)[:1][0]
        return latest_collection_point.collection_point
    collection_point = property(_get_latest_collection_point)

    def _get_latest_bag_quantities(self):
        latest_order = CustomerOrderChange.objects.order_by('-changed').filter(customer=self)[:1][0]
        return latest_order.bag_quantities#.all()[:1][0].bag_type.name
    bag_quantities = property(_get_latest_bag_quantities)

    def __str__(self):
        return '{} ({})'.format(self.full_name, self.nickname)


class AccountStatusChange(models.Model):
    AWAITING_DIRECT_DEBIT = 'AWAITING_DIRECT_DEBIT'
    #AWAITING_START_CONFIRMATION = 'AWAITING_START_CONFIRMATION'
    ACTIVE = 'ACTIVE'
    #ON_HOLD = 'HOLD'
    LEFT = 'LEFT'
    STATUS_CHOICES = (
        (AWAITING_DIRECT_DEBIT, 'Awating Go Cardless'),
        #(AWAITING_START_CONFIRMATION, 'Awating Start Confirmation'),
        (ACTIVE, 'Active'),
        #(ON_HOLD, 'On Hold'),
        (LEFT, 'Left'),
    )
    changed = models.DateTimeField(auto_now_add=True)
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
    changed = models.DateTimeField(auto_now_add=True)
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
        return 'Customer Collection Point Change for {} on {}'.format(
            self.customer.full_name,
            self.changed.strftime('%Y-%m-%d'),
        )


class CustomerOrderChange(models.Model):
    changed = models.DateTimeField(auto_now_add=True)
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
        verbose_name_plural = "customer order changes bag quantities"

    def __str__(self):
        return 'Customer Order Change Bag Quantity for {} chose {} {} at {}'.format(
            self.customer_order_change.customer.full_name,
            self.quantity,
            self.bag_type.name,
            self.customer_order_change.changed.strftime('%Y-%m-%d'),
        )
