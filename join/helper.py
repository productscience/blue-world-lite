from collections import OrderedDict
from datetime import timedelta
from django.utils import timezone
from django.contrib.humanize.templatetags.humanize import ordinal
import datetime
import pytz
import threading

from billing_week import (
    current_billing_week,
    get_billing_week,
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


def dates_affecting_collection(collection_point, datetime, billing_week):
    """
    Takes a collection point, the time, and current billing week, and returns
    strings for the collection date(s), the deadline for changes, and which
    collection any changes affect, based on whether we have passed the
    cut-off point
    """

    #   checks if we're past the cut off point in a billing week,
    #   and shows the correct dates for the week
    now = datetime
    weekday = now.weekday()
    bw = billing_week

    if weekday == 6:  # Sunday
        # dates = dates_affecting_collection(collection_point, now, bw)

        if timezone.now().hour < bw.end.hour:
            if collection_point.collection_day == 'WED':
                collection_date = friendly_date(bw.next().wed)
            elif collection_point.collection_day == 'THURS':
                collection_date = friendly_date(bw.next().thurs)
            else:
                collection_date = "{} and {}".format(
                    friendly_date(bw.next().wed),
                    friendly_date(bw.next().thurs))
            deadline = '3pm today'
            changes_affect = "next week's collection"
        else:
            if collection_point.collection_day == 'WED':
                collection_date = friendly_date(bw.wed)
            elif collection_point.collection_day == 'THURS':
                collection_date = friendly_date(bw.thurs)
            else:
                collection_date = "{} and {}".format(
                    friendly_date(bw.wed),
                    friendly_date(bw.thurs))
            deadline = '3pm next Sunday'
            changes_affect = "the collection after next"
    elif weekday == 0:  # Monday
        if collection_point.collection_day == 'WED':
            collection_date = friendly_date(bw.wed)
        elif collection_point.collection_day == 'THURS':
            collection_date = friendly_date(bw.thurs)
        else:
            collection_date = "{} and {}".format(
                friendly_date(bw.wed),
                friendly_date(bw.thurs))
        deadline = '3pm this Sunday'
        changes_affect = "next week's collection"
    elif weekday == 1:  # Tuesday
        if collection_point.collection_day == 'WED':
            collection_date = friendly_date(bw.wed)
        elif collection_point.collection_day == 'THURS':
            collection_date = friendly_date(bw.thurs)
        else:
            collection_date = "{} and {}".format(
                friendly_date(bw.wed),
                friendly_date(bw.thurs))
        deadline = '3pm this Sunday'
        changes_affect = "next week's collection"
    elif weekday == 2:  # Wednesday
        if collection_point.collection_day == 'WED':
            collection_date = friendly_date(bw.wed)
        elif collection_point.collection_day == 'THURS':
            collection_date = friendly_date(bw.thurs)
        else:
            collection_date = "{} and {}".format(
                friendly_date(bw.wed),
                friendly_date(bw.thurs))
        deadline = '3pm this Sunday'
        changes_affect = "next week's collection"
    elif weekday == 3:  # Thurs
        if collection_point.collection_day == 'WED':
            collection_date = friendly_date(bw.next().wed)
        elif collection_point.collection_day == 'THURS':
            collection_date = friendly_date(bw.thurs)
        else:
            # special case as it's open for two days
            collection_date = friendly_date(bw.thurs)
        deadline = '3pm this Sunday'
        changes_affect = "next week's collection"
    else:
        if collection_point.collection_day == 'WED':
            collection_date = friendly_date(bw.next().wed)
            # collection_date = 'Wednesday next week'
        elif collection_point.collection_day == 'THURS':
            collection_date = friendly_date(bw.next().thurs)
            # collection_date = 'Thursday next week'
        else:
            # collection_date = 'Wednesday and Thursday next week'
            collection_date = "{} and {}".format(
                friendly_date(bw.next().wed),
                friendly_date(bw.next().thurs))
        if weekday == 4:  # Friday
            deadline = '3pm this Sunday'
        else:  # Saturday
            deadline = '3pm tomorrow'
        changes_affect = "next week's collection"


    return {
        "collection_date": collection_date,
        "deadline": deadline,
        "changes_affect": changes_affect
        }
