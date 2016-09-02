
from django.test import TestCase
from django.utils import timezone

from .models import CollectionPoint

from .helper import collection_dates_for

from billing_week import get_billing_week

class TestDashboardHelpers(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.ofs = CollectionPoint.objects.create(name='The Old Fire Station',
            collection_day='WED')
        cls.mother_earth = CollectionPoint.objects.create(name='Mother Earth',
            collection_day='THURS')
        cls.black_cat = CollectionPoint.objects.create(name='Black Cat',
            collection_day='WED_THURS')

        # we're relying on the billing week class to give us the right dates
        cls.bw = get_billing_week(timezone.now())


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
