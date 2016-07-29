from collections import OrderedDict
from datetime import timedelta
from django.utils import timezone
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


def render_bag_quantities(obj):
    result = ''
    for bag_quantity in obj:
        result += '{} x {}\n'.format(
            bag_quantity.quantity,
            bag_quantity.bag_type.name,
        )
    return result
