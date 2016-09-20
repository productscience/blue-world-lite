
from django.test import TestCase
from django.utils import timezone

from .models import CollectionPoint

from .helper import collection_dates_for, get_next_billing_date

from billing_week import get_billing_week, billing_weeks_left_in_the_month

from freezegun import freeze_time

class TestDashboardCollectionPointHelpers(TestCase):

    def setUp(self):
        # Set up data for the whole TestCase
        self.ofs = CollectionPoint.objects.create(name='The Old Fire Station',
            collection_day='WED')
        self.mother_earth = CollectionPoint.objects.create(name='Mother Earth',
            collection_day='THURS')
        self.black_cat = CollectionPoint.objects.create(name='Black Cat',
            collection_day='WED_THURS')

        # we're relying on the billing week class to give us the right dates
        self.bw = get_billing_week(timezone.now())

    def test_returns_the_correct_date(self):
        self.assertEqual(
            collection_dates_for(self.bw, self.ofs),
            [self.bw.wed])
        self.assertEqual(
            collection_dates_for(self.bw, self.mother_earth),
            [self.bw.thurs])


    def test_returns_the_correct_date_with_two_collection_days(self):
        self.assertEqual(
            collection_dates_for(self.bw, self.black_cat),
            [self.bw.wed, self.bw.thurs])


class TestBillingDashboardHelpers(TestCase):

    @freeze_time("2016-09-14")
    def test_next_billing_month_for_short_month(self):
        # we'll check for september
        now = timezone.now()
        next_billing_date = get_next_billing_date(now).strftime("%Y-%m-%d")

        assert(next_billing_date == "2016-10-02")

    @freeze_time("2016-10-03")
    def test_next_billing_month_for_long_month(self):
        # we'll check for a October
        now = timezone.now()
        next_billing_date = get_next_billing_date(now).strftime("%Y-%m-%d")

        assert(next_billing_date == "2016-10-30")


    @freeze_time("2016-10-31")
    def test_next_billing_month_for_long_month(self):
        # we'll check for a November
        now = timezone.now()
        next_billing_date = get_next_billing_date(now).strftime("%Y-%m-%d")

        assert(next_billing_date == "2016-12-04")
