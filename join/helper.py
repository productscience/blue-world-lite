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


def get_pickup_dates(now=None, months=2):
    if now is None:
        now = timezone.now()
    wednesday = 2
    first_wednesday = _next_weekday(now, wednesday, 1000).replace(hour=0)
    ofirst_wednesday = _next_weekday(now, wednesday, 0).replace(hour=0)
    assert first_wednesday == ofirst_wednesday
    current_month = now.month
    current_year = now.year
    billing_dates = OrderedDict()
    d = datetime.datetime(
        current_year,
        current_month,
        1,
        0, 0, 0,
        tzinfo=timezone.get_default_timezone()
    )
    billing_dates[d] = [first_wednesday]
    allowed_months = [d]
    for x in range(months-1):
        current_month += 1
        if current_month == 13:
            current_month = 1
            current_year += 1
        allowed_months.append(
            datetime.datetime(
                current_year,
                current_month,
                1,
                0, 0, 0,
                tzinfo=timezone.get_default_timezone()
            )
        )
    assert len(allowed_months) == months
    next_wednesday = first_wednesday
    for x in range(months*5):
        next_wednesday = next_wednesday + timedelta(7)
        month = datetime.datetime(
            next_wednesday.year,
            next_wednesday.month,
            1,
            0, 0, 0,
            tzinfo=timezone.get_default_timezone()
        )
        if month not in allowed_months:
            break
        if month not in billing_dates:
            billing_dates[month] = [next_wednesday]
        else:
            billing_dates[month].append(next_wednesday)
    return billing_dates
