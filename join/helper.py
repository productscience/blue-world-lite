import threading


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


from django.utils import timezone
from datetime import timedelta
import datetime
from collections import OrderedDict


def next_deadline():
    sunday = 6
    return _next_weekday(timezone.now(), sunday, 15).replace(
        hour=15,
        minute=0,
        second=0,
        microsecond=0,
    )


def last_deadline():
    return next_deadline() - timedelta(7)


def next_collection():
    wednesday = 2
    a = _next_weekday(timezone.now(), wednesday, 12)
    return a


def _next_weekday(d, weekday, cutoff_hour):
    # The value of weekday is 0-6 where Monday is 0 and Sunday is 6
    days_ahead = weekday - d.weekday()
    if days_ahead == 0:
        if d.hour >= cutoff_hour:
            days_ahead += 7
    elif days_ahead < 0:  # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)


def start_of_the_month(now=None):
    if now is None:
        now = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return now - timedelta(days=now.day-1)


# XXX Lose the original timezone?
def get_minute(start):
    # return start.replace(second=0, microsecond=0)
    current_year = start.year
    current_month = start.month
    current_day = start.day
    current_hour = start.hour
    current_minute = start.minute
    return datetime.datetime(
        current_year,
        current_month,
        current_day,
        current_hour,
        current_minute,
        0,
        tzinfo=timezone.get_default_timezone()
    )


# XXX Lose the original timezone?
def get_month(start):
    #return start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_year = start.year
    current_month = start.month
    return datetime.datetime(
        current_year,
        current_month,
        1,
        0, 0, 0,
        tzinfo=timezone.get_default_timezone()
    )


def get_day(start):
    # return start.replace(hour=0, minute=0, second=0, microsecond=0)
    current_year = start.year
    current_month = start.month
    current_day = start.day
    return datetime.datetime(
        current_year,
        current_month,
        current_day,
        0, 0, 0,
        tzinfo=timezone.get_default_timezone()
    )


def get_pickup_dates(now=None, months=2, last=None):
    if now is None:
        now = timezone.now()
    wednesday = 2
    first_wednesday = _next_weekday(now, wednesday, 1000).replace(hour=0)
    # ofirst_wednesday = _next_weekday(now, wednesday, 0).replace(hour=0)
    # assert first_wednesday == ofirst_wednesday
    billing_dates = OrderedDict()
    cur_month = now.month
    cur_year = now.year
    d = get_month(now)
    billing_dates[d] = [first_wednesday]
    allowed_months = [d]
    if months is None:
        months = 10000
    for x in range(months-1):
        cur_month += 1
        if cur_month == 13:
            cur_month = 1
            cur_year += 1
        next_month = datetime.datetime(
            cur_year,
            cur_month,
            1,
            0, 0, 0,
            tzinfo=timezone.get_default_timezone()
        )
        if last is not None:
            if next_month == get_month(last):
                break
        else:
            allowed_months.append(next_month)
    if last is None:
        assert len(allowed_months) == months
    next_wednesday = first_wednesday
    for x in range(months*5):
        next_wednesday = next_wednesday + timedelta(7)
        month = get_month(next_wednesday)
        if month not in allowed_months:
            break
        if month not in billing_dates:
            billing_dates[month] = [next_wednesday]
        else:
            billing_dates[month].append(next_wednesday)
    return billing_dates


def render_bag_quantities(obj):
    result = ''
    for bag_quantity in obj:
        result += '{} x {}\n'.format(
            bag_quantity.quantity,
            bag_quantity.bag_type.name,
        )
    return result
