from django.db import models
from django.conf import settings


class CollectionPoint(models.Model):
    name = models.CharField(max_length=40, help_text="e.g. 'The Old Fire Station'. <b>IMPORTANT</b>: Due to a limitation you <b>cannot use non-standard characters like accents</b> - sorry. If you do, you form will not display and you might get a strange error.")
    location = models.CharField(null=True, blank=True, max_length=100, help_text="E.g. 'Leswin Road, N16'")
    latitude = models.FloatField(null=True, blank=True, help_text="Allows your pickup to show on a map. Latitude should be between 49 and 60 in the UK. You can find latitude and longitude by following these instructions: <ol><li>Go to <a href='http://maps.google.co.uk/' target='_NEW'>Google maps</a></li><li>Click the tiny green flask icon on the top-right</li><li>Scroll down and enable the 'LatLng Tool Tip'</li><li>Find your pickup and zoom in close</li><li>You'll see (latitude, longitude) showing on the mouse pointer</li><li>Note them down and copy latitude into the field above and longitude into the field below</li></ol>")
    longitude = models.FloatField(null=True, blank=True, help_text="Longitude should be between -10 and 2 in the UK")
    active = models.BooleanField(default=True, help_text="You can mark this pickup as not available at the moment if you need to")
    display_order = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['display_order']


class BagType(models.Model):
    """Each group has some bag types defined so that their customers can select them from the joining form"""
    name = models.CharField(max_length=50, help_text="E.g. 'Standard veg'.")
    weekly_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True,blank=True, help_text="Enter the weekly fee for receiving this bag.", verbose_name="Weekly cost")
    display_order = models.IntegerField(null=True, blank=True, help_text="Bags will be sorted by this number (though they will always be grouped into fruit or veg first)")
    active = models.BooleanField(default=True, help_text="Active bags appear in the joining form.")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['display_order']


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


class AccountStatusChange(models.Model):
    AWAITING_DIRECT_DEBIT = 'AWAITING_DIRECT_DEBIT'
    AWAITING_START_CONFIRMATION = 'AWAITING_START_CONFIRMATION'
    ACTIVE = 'ACTIVE'
    ON_HOLD = 'HOLD'
    LEFT = 'LEFT'
    STATUS_CHOICES = (
        (AWAITING_DIRECT_DEBIT, 'Awating Go Cardless'),
        (AWAITING_START_CONFIRMATION, 'Awating Start Confirmation'),
        (ACTIVE, 'Active'),
        (ON_HOLD, 'On Hold'),
        (LEFT, 'Left'),
    )
    changed = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(
        Customer,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
    )
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)


class CollectionPointChange(models.Model):
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


class OrderChange(models.Model):
    changed = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(
        Customer,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
    )

class BagQuantity(models.Model):
    order_change = models.ForeignKey(
        OrderChange,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
    )
    bag_type = models.ForeignKey(
        BagType,
        # XXX Not sure about this yet
        on_delete=models.CASCADE,
    )
    quantity = models.IntegerField()
