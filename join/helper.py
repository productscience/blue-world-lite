from collections import OrderedDict
from datetime import timedelta
from django.utils import timezone
from django.contrib.humanize.templatetags.humanize import ordinal
import datetime
import pytz
import threading

from billing_week import (
    get_billing_week
)

_thread_locals = threading.local()


def get_current_request():
    return getattr(_thread_locals, 'request', None)


class ThreadLocals(object):
    """
    Middleware that gets various objects from the
    request object and saves them in thread local storage.
    """
    def process_request(self, request):
        _thread_locals.request = request


def get_pickup_dates(start, stop, month_start=False):
    if isinstance(start, datetime.date):
        start = pytz.utc.localize(
            datetime.datetime(start.year, start.month, start.day, 12)
        )
    bw = get_billing_week(start)
    if month_start:
        while bw.week != 1:
            next_start = bw.start - timedelta(days=6, hours=1)
            bw = get_billing_week(next_start)
    counter = 1
    result = OrderedDict()
    result[datetime.date(bw.year, bw.month, 1)] = [bw]
    while counter < 1000:
        if isinstance(stop, int):
            if counter == stop:
                return result
        else:
            if bw.start > stop:
                return result
        bw = get_billing_week(bw.end + timedelta(hours=1))
        d = datetime.date(bw.year, bw.month, 1)
        if d not in result:
            result[d] = []
        result[d].append(bw)
        counter += 1
    raise Exception(
        'Found more than 1000 or so pickup dates, perhaps there is a problem?'
    )


def render_bag_quantities(bag_quantities):
    result = ''
    for bag_quantity in bag_quantities:
        result += '{} x {}\n'.format(
            bag_quantity.quantity,
            bag_quantity.bag_type.name,
        )
    return result


def calculate_weekly_fee(bag_quantities):
    amount = 0
    for bag_quantity in bag_quantities:
        amount += bag_quantity.quantity * bag_quantity.bag_type.weekly_cost
    return amount

def friendly_date(date):
    """
    Accepts a datetime object and returns a string with ordinalised dates, like
    Wednesday 20th July, or Thursday 21st August
    """

    friendly_date = "{} {} {}".format(
        date.strftime("%A"),
        ordinal(date.strftime("%d")),
        date.strftime("%B"))

    return friendly_date


def collection_dates_for(bw, collection_point):
    """
    Returns a list of zero or more collection dates for a given collection point,
    and billing week.
    """

    collection_dates = []

    if collection_point.collection_day == 'WED':
        collection_dates.append(bw.wed)
    elif collection_point.collection_day == 'THURS':
        collection_dates.append(bw.thurs)
    elif collection_point.collection_day == "WED_THURS":
        collection_dates.append(bw.wed)
        collection_dates.append(bw.thurs)

    return collection_dates


def customer_ids_by_status(query_value):
    """
    Should this be part of a model manager?
    We're having to import inside a method, so probably
    """
    from join.models import AccountStatusChange

    ascs = AccountStatusChange.objects.order_by(
        'customer', '-changed'
    ).distinct('customer')

    customer_ids = [
        c.customer_id for c in ascs if c.status == query_value
    ]

    return customer_ids

def customer_ids_on_holiday_for_billing_week(billing_week):
    """
    Accepts a list of customer ids, and returns the list of ids where
    the customer is away for the given billing week
    """
    from join.models import Skip

    skipped_customer_ids = Skip.objects.filter(
        billing_week=billing_week
    ).only('customer_id').values_list('customer_id')

    return skipped_customer_ids

def effective_billing_week(billing_week, time):
    """
    Accepts a billing week, and a date, and returns the 'effective' billing week
    based on whether we're before or after the Wednesday in the week.
    """

    wednesday = datetime.datetime(
        billing_week.wed.year,
        billing_week.wed.month,
        billing_week.wed.day,
        tzinfo=timezone.get_current_timezone())

    if time < wednesday:
        return billing_week
    else:
        return billing_week.next()
