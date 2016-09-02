"""
(c) 2016 James Gardner
MIT License
Will be moved into its own package.
"""
import datetime
from django.utils.timezone import is_aware
from django.utils import timezone
from datetime import timedelta
import pytz


def first_wed_of_month(year, month):
    first_day_of_month = datetime.date(year, month, 1)
    if first_day_of_month.weekday() == 2:
        return first_day_of_month
    else:
        days_until_wed = 2 - first_day_of_month.weekday()
        if days_until_wed < 0:
            days_until_wed += 7
        return first_day_of_month + timedelta(days_until_wed)


def in_dst(dt):
    if str(dt.utcoffset()) == '1:00:00':
        return True
    else:
        return False


def current_billing_week():
    # UTC
    return get_billing_week(timezone.now())


def get_billing_week(d, _recursively_called=False):
    """
    Find the billing week a particular time occurs in
    """
    # WARNING: Do not change this function. Ever.
    #          All the logic of the entire application depends on it
    #          including invoice generation etc.
    #          By changing this function, you will re-write the history
    #          of what happened in the past, as well as behaviour in future
    #          If you must change it, keep this implementation for dates
    #          up until the date you change it, and use your new
    #          implementation for dates in the future to make sure you
    #          dont accidentally re-write history.
    deadline_tz = pytz.timezone("Europe/London")
    # Make sure it is a datetime with the correct timezone
    assert isinstance(d, datetime.datetime), \
        'Expected datetime, not {!r}'.format(d)
    assert is_aware(d), \
        'No timezone information supplied for date: {!r}'.format(d)
    # assert d.tzinfo == pytz.UTC, \
    #     'Expected UTC timezone for date: {!r}'.format(d)
    first_wed = first_wed_of_month(d.year, d.month)
    first_sunday = first_wed - timedelta(3)
    counter = 0
    while counter < 7:
        # Have to add the 7 days before adding the time to account for timezone
        # differences
        start_of_billing_week = deadline_tz.localize(
            datetime.datetime.combine(
                first_sunday + timedelta(7*counter),
                datetime.time(15, 0, 0, 0)
            ), is_dst=None
        ).astimezone(pytz.utc)
        if counter == 0 and d < start_of_billing_week:
            if _recursively_called:
                raise Exception("Date led to recursion, this is the new date: {}".format(d))
            return get_billing_week(deadline_tz.localize(datetime.datetime(d.year, d.month,1)-timedelta(1)), True)
        end_of_billing_week = deadline_tz.localize(
            datetime.datetime.combine(
                first_sunday + timedelta(7*(counter+1)),
                # datetime.time(14, 59, 59,1000000-1)
                datetime.time(15, 0, 0, 0)
            ),
            is_dst=None
        ).astimezone(pytz.utc)
        counter += 1
        if d > end_of_billing_week:
            continue
        if in_dst(start_of_billing_week):
            start_of_billing_week = start_of_billing_week - timedelta(hours=1)
        if in_dst(end_of_billing_week):
            end_of_billing_week = end_of_billing_week - timedelta(hours=1)
        if d >= start_of_billing_week and d < end_of_billing_week:
            # We have a matching week in this calendar month, but it is
            # possible it is actually part of next month's billing cycle
            # e.g. 31st Jan 2017 is a Feb billing week
            wed = (start_of_billing_week + timedelta(3)).date()
            if (wed.year, wed.month) > (start_of_billing_week.year, start_of_billing_week.month):
                # The wed month and year are the same as the end date one
                return BillingWeek(
                    wed,
                    1,
                    start_of_billing_week,
                    end_of_billing_week,
                )
            # The wed month and year are the same as the end date one
            return BillingWeek(
                wed,
                counter,
                start_of_billing_week,
                end_of_billing_week,
            )
    raise Exception('Did not find billing week: {!r}'.format(d))


class BillingWeek(object):
    """\
    A week whose Wednesday falls within a particular calendar month, and which
    runs from 3pm Sunday to 2:59:59.999999 the following Sunday in the
    Europe/London timezone.

    This definition means that billing weeks that span the clocks going back
    are shorter, and those that span the clocks going forward are longer.

    It also means that billing weeks can start or end in a month that isn't
    their billing month, because their Wednesday's can be very close to the
    start or end of the calendar month.
    """

    def __init__(self, wed, week, start=None, end=None):
        self.year = wed.year
        self.month = wed.month
        self.week = int(week)
        if start is not None:
            assert isinstance(start, datetime.datetime), \
                'Expected start to be a datetime, not {!r}'.format(start)
        if end is not None:
            assert isinstance(end, datetime.datetime), \
                'Expected end to be a datetime, not {!r}'.format(end)
        assert isinstance(wed, datetime.date)
        self.wed = wed
        self._start = start
        self._end = end
        self._mon = None
        self._thurs = None
        self._sun = None
        self._next = None
        self._prev = None
        self._next_month = None
        self._prev_month = None

    def _get_start(self):
        if not self._start:
            deadline_tz = pytz.timezone("Europe/London")
            self._start = deadline_tz.localize(
                datetime.datetime.combine(
                    self.wed - timedelta(3),
                    datetime.time(15, 0, 0, 0)
                ), is_dst=None
            ).astimezone(pytz.utc)
            if in_dst(self._start):
                self._start = self._start - timedelta(hours=1)
        return self._start
    start = property(_get_start)

    def _get_end(self):
        if not self._end:
            deadline_tz = pytz.timezone("Europe/London")
            self._end = deadline_tz.localize(
                datetime.datetime.combine(
                    self.wed + timedelta(4),
                    datetime.time(15, 0, 0, 0)
                ), is_dst=None
            ).astimezone(pytz.utc)
            if in_dst(self._end):
                self._end = self._end - timedelta(hours=1)
        return self._end
    end = property(_get_end)

    def _get_mon(self):
        if not self._mon:
            self._mon = self.wed - timedelta(2)
        return self._mon
    mon = property(_get_mon)

    def _get_thurs(self):
        if not self._thurs:
            self._thurs = self.wed + timedelta(1)
        return self._thurs
    thurs = property(_get_thurs)

    def _get_sun(self):
        if not self._sun:
            self._sun = self.wed + timedelta(4)
        return self._sun
    sun = property(_get_sun)

    def next(self):
        if not self._next:
            # Should be fine, since the end is treated
            # as the start of the next week
            self._next = get_billing_week(self.end)
        return self._next

    def next_month(self):
        if not self._next_month:
            month = self.wed.month
            year = self.wed.year
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1
            self._next_month = datetime.date(year, month, 1)
        return self._next_month

    def prev_month(self):
        if not self._prev_month:
            month = self.wed.month
            year = self.wed.year
            if month == 1:
                month = 12
                year -= 1
            else:
                month -= 1
            self._prev_month = datetime.date(year, month, 1)
        return self._prev_month

    def prev(self):
        if not self._prev:
            self._prev = get_billing_week(self.start - timedelta(1))
        return self._prev

    def __str__(self):
        return '{0}-{1:02d} {2}'.format(self.year, self.month, self.week)

    def __repr__(self):
        return '<BillingWeek {}>'.format(str(self))

    def __lt__(self, other):
        return str(self) < str(other)

    def __le__(self, other):
        return str(self) <= str(other)

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)

    def __gt__(self, other):
        return str(self) > str(other)

    def __ge__(self, other):
        return str(self) >= str(other)

    def __hash__(self):
        return int('{0}{1:02d}{2}'.format(self.year, self.month, self.week))


def billing_weeks_left_in_the_month(billing_week_string):
    """
    Takes a list, billing week
    """
    weeks_left = []
    starting_week = parse_billing_week(billing_week_string)

    def billing_weeks_left(weeks, start_bw, bw):
                # skip the same week
                if start_bw == bw:
                    return billing_weeks_left(weeks, start_bw, bw.next())
                elif start_bw.month == bw.month:
                    weeks.append(bw)
                    return billing_weeks_left(weeks, start_bw, bw.next())
                else:
                    return weeks

    return billing_weeks_left(weeks_left, starting_week, starting_week)



def parse_billing_week(billing_week_string):
    """Takes a billing week string and returns a BillingWeek object."""
    year = int(billing_week_string[:4])
    month = int(billing_week_string[5:7])
    week = int(billing_week_string[8])
    if week > 5:
        raise ValueError("Months cannot have more than 5 billing weeks")
    first_wed = first_wed_of_month(year, month)
    our_wed = first_wed+timedelta((week-1)*7)
    if first_wed.month != our_wed.month:
        raise ValueError('No week {} in this billing month'.format(week))
    assert isinstance(first_wed, datetime.date)
    return BillingWeek(
        our_wed,
        week,
    )

def next_n_billing_weeks(n, bw, billing_weeks=[]):
    """
    Takes a number of billing weeks and a starting billing week, and returns
    a list of billing weeks
    """
    if n > len(billing_weeks):
        billing_weeks.append(bw.next())
        return next_n_billing_weeks(n, bw.next(), billing_weeks)
    else:
        return billing_weeks

def prev_n_billing_weeks(n, bw, billing_weeks=[]):
    if n > len(billing_weeks):
        billing_weeks.append(bw.prev())
        return prev_n_billing_weeks(n, bw.prev(), billing_weeks)
    else:
        return billing_weeks


def next_valid_billing_week(bw, billing_week_strings):
    """
    Takes a billing week, and a set of skipped billing weeks, and steps forward
    until it finds a week that isni't in the skipped set
    """
    if str(bw) in billing_week_strings:
        return next_valid_billing_week(bw.next(), billing_week_strings)
    else:
        return bw


if __name__ == '__main__':

    import unittest

    class TestBillingWeek(unittest.TestCase):
        def test_comparison(self):
            first = parse_billing_week('2017-07 1')
            also_first = parse_billing_week('2017-07 1')
            second = parse_billing_week('2017-07 2')

            self.assertTrue(first < second)
            self.assertFalse(second < first)
            self.assertFalse(first < also_first)

            self.assertTrue(first <= second)
            self.assertTrue(first <= also_first)
            self.assertFalse(second <= first)

            self.assertTrue(first == also_first)
            self.assertFalse(first == second)

            self.assertFalse(first != also_first)
            self.assertTrue(first != second)

            self.assertFalse(first > second)
            self.assertTrue(second > first)
            self.assertFalse(first > also_first)

            self.assertFalse(first >= second)
            self.assertTrue(first >= also_first)
            self.assertTrue(second >= first)

        def test_timezone_behaviour(self):
            tz = pytz.timezone("Europe/London")
            summer = datetime.datetime(2017, 7, 17, 15)
            winter = datetime.datetime(2017, 1, 17, 15)
            for date in [summer, winter]:
                for is_dst in [True, False, None]:
                    is_winter = winter == date
                    d = tz.localize(date, is_dst=is_dst)
                    # print('is_winter', is_winter, 'is_dst', is_dst)
                    # print(d)
                    # print(d.utcoffset())
                    # print(d.astimezone(pytz.utc))
                    if is_winter:
                        self.assertEqual(str(d.utcoffset()), '0:00:00')
                        self.assertEqual(str(d.astimezone(pytz.utc)), '2017-01-17 15:00:00+00:00')
                        self.assertFalse(in_dst(d))
                    else:
                        self.assertEqual(str(d.utcoffset()), '1:00:00')
                        self.assertEqual(str(d.astimezone(pytz.utc)), '2017-07-17 14:00:00+00:00')
                        self.assertTrue(in_dst(d))

        def test_first_wed_of_the_month(self):
            test_case = [
                (1, (2017, 2)),
                (2, (2016, 11)),
                (3, (2017, 5)),
                (4, (2017, 1)),
                (5, (2016, 10)),
                (6, (2016, 7)),
                (7, (2016, 9)),
            ]
            for expected_day, date in test_case:
                year, month = date
                result = first_wed_of_month(year, month)
                self.assertEqual(result.year, year)
                self.assertEqual(result.month, month)
                self.assertIsInstance(result, datetime.date)
                self.assertEqual(result.day, expected_day)

        def test_properties(self):
            utc = pytz.timezone("UTC")
            bw = get_billing_week(utc.localize(datetime.datetime(2017, 2, 1, 17)))
            self.assertEqual(bw.start, utc.localize(datetime.datetime(2017, 1, 29, 15)))
            # self.assertEqual(bw.end, utc.localize(datetime.datetime(2017, 2, 5, 14, 59, 59, 1000000-1)))
            self.assertEqual(bw.end, utc.localize(datetime.datetime(2017, 2, 5, 15, 0, 0, 0)))
            self.assertEqual(bw.mon, datetime.date(2017, 1, 30))
            self.assertEqual(bw.wed, datetime.date(2017, 2, 1))
            self.assertEqual(bw.thurs, datetime.date(2017, 2, 2))
            self.assertEqual(bw.sun, datetime.date(2017, 2, 5))
            self.assertEqual(bw.next().start, utc.localize(datetime.datetime(2017, 2, 5, 15, 0, 0, 0)))
            self.assertEqual(bw.next().prev().start, utc.localize(datetime.datetime(2017, 1, 29, 15)))

            self.assertEqual(bw.next_month(), datetime.date(2017, 3, 1))
            self.assertEqual(bw.prev_month(), datetime.date(2017, 1, 1))
            nbw = get_billing_week(utc.localize(datetime.datetime(2017, 12, 30, 17)))
            self.assertEqual(nbw.next_month(), datetime.date(2018, 1, 1))
            nbw = get_billing_week(utc.localize(datetime.datetime(2018, 1, 5, 17)))
            self.assertEqual(nbw.prev_month(), datetime.date(2017, 12, 1))

        def test_get_billing_week(self):
            utc = pytz.timezone("UTC")
            # Test all the Wednesdays in Feb 2017 collections
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2017, 2, 1, 17),  is_dst=None))), '2017-02 1')
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2017, 2, 8, 17),  is_dst=None))), '2017-02 2')
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2017, 2, 15, 17), is_dst=None))), '2017-02 3')
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2017, 2, 22, 17), is_dst=None))), '2017-02 4')
            # Test all the Thursdays in Feb 2017 collections
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2017, 2, 2, 17),  is_dst=None))), '2017-02 1')
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2017, 2, 9, 17),  is_dst=None))), '2017-02 2')
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2017, 2, 16, 17), is_dst=None))), '2017-02 3')
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2017, 2, 23, 17), is_dst=None))), '2017-02 4')
            # Test all the Tuesdays in Feb 2017 collections
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2017, 1, 31, 17), is_dst=None))), '2017-02 1')
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2017, 2, 7, 17),  is_dst=None))), '2017-02 2')
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2017, 2, 14, 17), is_dst=None))), '2017-02 3')
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2017, 2, 21, 17), is_dst=None))), '2017-02 4')

            # Other potentially tricky dates
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2017, 1, 30, 17), is_dst=None))), '2017-02 1')
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2017, 1, 29, 12), is_dst=None))), '2017-01 4')
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2017, 1, 29, 17), is_dst=None))), '2017-02 1')

            # Now check what happens one microsecond before, on and after a deadline t ime
            # Winter
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2017, 1, 29, 14, 59, 59, 1000000-1), is_dst=None))), '2017-01 4')
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2017, 1, 29, 15), is_dst=None))), '2017-02 1')
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2017, 1, 29, 15, 1), is_dst=None))), '2017-02 1')
            # Summer
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2017, 7, 30, 13, 59, 59, 1000000-1), is_dst=None))), '2017-07 4')
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2017, 7, 30, 14), is_dst=None))), '2017-08 1')
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2017, 7, 30, 14, 1), is_dst=None))), '2017-08 1')
            # Starting with a european timezone
            london = pytz.timezone("Europe/London")
            self.assertEqual(str(get_billing_week(london.localize(datetime.datetime(2017, 7, 30, 14, 59, 59, 1000000-1), is_dst=None))), '2017-07 4')
            self.assertEqual(str(get_billing_week(london.localize(datetime.datetime(2017, 7, 30, 15), is_dst=None))), '2017-08 1')
            self.assertEqual(str(get_billing_week(london.localize(datetime.datetime(2017, 7, 30, 15, 1), is_dst=None))), '2017-08 1')

        def test_start_and_end_times_over_clock_change_weeks(self):
            # In 2017 the clocks change as follows:
            # Sunday, March 26, 1:00 AM       Sunday, October 29, 2:00 AM

            utc = pytz.timezone("UTC")
            london = pytz.timezone("Europe/London")

            # Check the clocks going forward in the spring:
            self.assertRaises(pytz.exceptions.NonExistentTimeError, london.localize, datetime.datetime(2017, 3, 26, 1, 30), is_dst=None)
            just_before_clocks_go_forward = get_billing_week(utc.localize(datetime.datetime(2017, 3, 26, 0, 59),  is_dst=None))
            just_after_clocks_go_forward = get_billing_week(utc.localize(datetime.datetime(2017, 3, 26, 1, 1),  is_dst=None))
            self.assertEqual(str(just_before_clocks_go_forward), '2017-03 4')
            self.assertEqual(str(just_after_clocks_go_forward), '2017-03 4')
            self.assertEqual(just_before_clocks_go_forward.start, just_after_clocks_go_forward.start)
            self.assertEqual(just_before_clocks_go_forward.start.utcoffset(), just_after_clocks_go_forward.start.utcoffset())
            self.assertEqual(just_before_clocks_go_forward.end, just_after_clocks_go_forward.end)
            self.assertEqual(just_before_clocks_go_forward.end.utcoffset(), just_after_clocks_go_forward.end.utcoffset())
            self.assertEqual('6 days, 23:00:00', str(just_before_clocks_go_forward.end - just_before_clocks_go_forward.start))

            # Check the clocks going back in the autumn
            self.assertRaises(pytz.exceptions.AmbiguousTimeError, london.localize, datetime.datetime(2017, 10, 29, 1, 30), is_dst=None)
            just_before_clocks_go_backwards = get_billing_week(utc.localize(datetime.datetime(2017, 10, 29, 0, 59), is_dst=None))
            just_after_clocks_go_backwards = get_billing_week(utc.localize(datetime.datetime(2017, 10, 29, 1, 1), is_dst=None))
            self.assertEqual(str(just_before_clocks_go_backwards), '2017-10 4')
            self.assertEqual(str(just_after_clocks_go_backwards), '2017-10 4')
            self.assertEqual(just_before_clocks_go_backwards.start, just_after_clocks_go_backwards.start)
            self.assertEqual(just_before_clocks_go_backwards.start.utcoffset(), just_after_clocks_go_backwards.start.utcoffset())
            self.assertEqual(just_before_clocks_go_backwards.end, just_after_clocks_go_backwards.end)
            self.assertEqual(just_before_clocks_go_backwards.end.utcoffset(), just_after_clocks_go_backwards.end.utcoffset())
            self.assertEqual('7 days, 1:00:00', str(just_before_clocks_go_backwards.end - just_before_clocks_go_backwards.start))

        def test_corners(self):
            utc = pytz.timezone("UTC")
            # Test all the Wednesdays in Feb 2017 collections
            bw = get_billing_week(utc.localize(datetime.datetime(2016, 8, 31, 17),  is_dst=None))
            self.assertEqual(str(bw), '2016-08 5')
            bw = get_billing_week(utc.localize(datetime.datetime(2017, 2, 1, 17),  is_dst=None))
            self.assertEqual(str(bw), '2017-02 1')

        def test_parse_billing_week(self):
            utc = pytz.timezone("UTC")
            self.assertEqual(parse_billing_week('2017-02 1').start, utc.localize(datetime.datetime(2017, 1, 29, 15)))
            # self.assertEqual(parse_billing_week('2017-02 1').end, utc.localize(datetime.datetime(2017,2,5,14,59,59,1000000-1)))
            self.assertEqual(parse_billing_week('2017-02 1').end, utc.localize(datetime.datetime(2017, 2, 5, 15, 0, 0, 0)))
            self.assertRaises(ValueError, parse_billing_week, '2017-07-6')
            self.assertRaises(ValueError, parse_billing_week, '2017-07-5')
            self.assertEqual(parse_billing_week('2016-08 1').wed, datetime.date(2016, 8, 3))

        def test_freezegun(self):
            utc = pytz.timezone("UTC")
            self.assertEqual(first_wed_of_month(2016, 7), datetime.date(2016, 7, 6))
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2016, 7, 1, 11)))), '2016-06 5')
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2016, 7, 2, 11)))), '2016-06 5')
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2016, 7, 3, 11)))), '2016-06 5')
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2016, 7, 3, 16)))), '2016-07 1')
            import freezegun
            with freezegun.freeze_time('2016-07-01 11:00', tick=False):
                self.assertEqual(str(get_billing_week(timezone.now())), '2016-06 5')
            self.assertEqual(str(get_billing_week(utc.localize(datetime.datetime(2016, 8, 2, 11)))), '2016-08 1')

        def test_hash(self):
            from collections import OrderedDict
            billing_weeks = OrderedDict()
            billing_weeks[parse_billing_week('2016-06 5')] = 1
            billing_weeks[parse_billing_week('2016-06 3')] = 1
            billing_weeks[parse_billing_week('2016-06 3')] += 1
            self.assertEqual(billing_weeks, OrderedDict([(parse_billing_week('2016-06 5'), 1), (parse_billing_week('2016-06 3'), 2)]))

        def test_brute(self):
            utc = pytz.timezone("UTC")
            # Let's just check we can get a billing date for every 30 mins in
            # the next 10 years, and that they are all in order

            s = utc.localize(datetime.datetime(2012, 5, 1, 0))
            s_12 = utc.localize(datetime.datetime(2012, 5, 1, 12))
            half_day_later = s + timedelta(minutes=60*12)
            assert s_12 == half_day_later
            self.assertEqual(str(get_billing_week(s)), '2012-05 1')
            self.assertEqual(str(get_billing_week(s_12)), '2012-05 1')
            self.assertEqual(str(get_billing_week(half_day_later)), '2012-05 1')

            from collections import OrderedDict

            for mins in [60*12]:
                billing_weeks = OrderedDict()
                first = utc.localize(datetime.datetime(2012, 1, 1, 16)) # Start of billing week
                end = utc.localize(datetime.datetime(2022, 1, 1, 16))
                start = first - timedelta(minutes=mins)
                last_bw = get_billing_week(start)
                last_pw = parse_billing_week(str(last_bw))
                while start <= end:
                    orig = start
                    start = start + timedelta(minutes=mins)
                    bw = get_billing_week(start)
                    self.assertGreaterEqual(bw, last_bw)
                    if bw not in billing_weeks:
                        billing_weeks[bw] = 0
                    billing_weeks[bw] += 1
                    if bw != last_bw:
                         pw = parse_billing_week(str(bw))
                         self.assertEqual(pw, bw)
                         self.assertGreater(pw, last_pw)
                         last_pw = pw
                    last_bw = bw
                for i, bwkey in enumerate(billing_weeks):
                    self.assertEqual(billing_weeks[bwkey], 14)
                self.assertEqual(len(billing_weeks), (((end-first).days)+1)/7.0)

        def test_billing_weeks_left_in_month(self):
            # we know there were 4 billing weeks after the first one in May 2016
            self.assertEqual(len(
                billing_weeks_left_in_the_month("2016-05 1")), 3)
            # we also know there were 3 billing weeks after the first on in
            # June
            self.assertEqual(len(
                billing_weeks_left_in_the_month("2016-06 1")), 4)

        def test_next_n_billing_weeks_returns_right_no_of_billing_weeks(self):
            utc = pytz.timezone("UTC")
            s = utc.localize(datetime.datetime(2016, 9, 2, 0))
            last_bw_in_aug = get_billing_week(s)
            self.assertEqual(
                len(next_n_billing_weeks(5, last_bw_in_aug)), 5)

        def test_prev_n_billing_weeks_returns_next_billing_week(self):
            utc = pytz.timezone("UTC")
            s = utc.localize(datetime.datetime(2016, 9, 2, 0))
            last_bw_in_aug = get_billing_week(s)
            self.assertNotIn(
                last_bw_in_aug,
                prev_n_billing_weeks(5, last_bw_in_aug))

        def test_prev_n_billing_weeks_returns_right_no_of_billing_weeks(self):
            utc = pytz.timezone("UTC")
            s = utc.localize(datetime.datetime(2016, 9, 2, 0))
            last_bw_in_aug = get_billing_week(s)
            self.assertEqual(
                len(prev_n_billing_weeks(5, last_bw_in_aug)), 5)




    unittest.main()
