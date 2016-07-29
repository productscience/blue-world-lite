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
    d = datetime.date(year, month, 1)
    first_day_of_month = d - timedelta(days=d.day-1)
    if first_day_of_month.weekday() == 2:
        return d
    else:
        days_until_wed = 2 - first_day_of_month.weekday()
        if days_until_wed < 0:
            days_until_wed += 7
        return d + timedelta(days_until_wed)


def in_dst(dt):
    if str(dt.utcoffset()) == '1:00:00':
        return True
    else:
        return False


def current_billing_week():
    # UTC
    return get_billing_week(timezone.now())


def get_billing_week(d):
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
            # print(start_of_billing_week,  end_of_billing_week, d, wed.strftime('%c'))
            if (start_of_billing_week + timedelta(3)).month > start_of_billing_week.month:
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
        return '<BillingWeek {} at {}>'.format(str(self), id(self))

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

    unittest.main()
