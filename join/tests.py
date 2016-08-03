"""
The DB user needs permission to create the test_blueworld database:

::

    ALTER USER blueworld CREATEDB;
"""

import pytz
import datetime
from collections import OrderedDict

from django.contrib.auth import models
from django.test import TestCase, TransactionTestCase
import freezegun

from billing_week import get_billing_week, parse_billing_week
from join.admin import packing_list
from join.models import CollectionPoint, CustomerCollectionPointChange
from join.models import Customer, BagType

from unittest import TestCase
TestCase.maxDiff = None
import unittest; unittest.util._MAX_LENGTH=1000


class DistinctOnBehaviourTestCase(TestCase):
    """
    Our billing change model relies on ditinct on working predictably in
    Django.

    This test just makes sure Django is generating the SQL we expect and
    returning the data we expect.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with freezegun.freeze_time('2016-07-01 11:00', tick=False):
            cp1 = CollectionPoint.objects.create(pk=1, name="Distinct First")
            cp2 = CollectionPoint.objects.create(pk=2, name="Distinct Second")
            cp3 = CollectionPoint.objects.create(pk=3, name="Distinct Third")
            customer1 = Customer.objects.create_now(pk=1, full_name='One')
        with freezegun.freeze_time('2016-07-01 12:00', tick=False):
            customer1.collection_point = cp1
        with freezegun.freeze_time('2016-07-01 12:30', tick=False):
            customer1.collection_point = cp2
        with freezegun.freeze_time('2016-07-21 13:00', tick=False):
            customer1.collection_point = cp3

    def test_distinct_on(self):
        self.assertEqual(
            tuple(
                CustomerCollectionPointChange.objects
                .order_by('customer', '-changed')
                .values_list('collection_point__name', flat=True)
            ),
            ('Distinct Third', 'Distinct Second', 'Distinct First')
        )
        self.assertEqual(
            tuple(
                CustomerCollectionPointChange.objects
                .order_by('customer', '-changed')
                .distinct('customer')
                .values_list('collection_point__name', flat=True)
            ),
            ('Distinct Third',)
        )
        self.assertEqual(
            tuple(
                CustomerCollectionPointChange.objects
                .order_by('customer', '-changed')
                .filter(
                    changed__lt=datetime.datetime(
                        2016, 7, 1, 12, 45,
                        tzinfo=pytz.utc
                    )
                )
                .distinct('customer')
                .values_list('collection_point__name', flat=True)
            ),
            ('Distinct Second',)
        )


class DistinctOnSubQueryBehaviourTestCase(TestCase):
    """
    Our billing change model relies on ditinct on working predictably in
    Django.

    This test just makes sure Django is generating the SQL we expect and
    returning the data we expect.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with freezegun.freeze_time(str(parse_billing_week('2016-06 1').wed)):
            cls.cp1 = CollectionPoint.objects.create(pk=21, name="First")
            cls.cp2 = CollectionPoint.objects.create(pk=22, name="Second")
            cls.cp3 = CollectionPoint.objects.create(pk=23, name="Third")
            cls.large_veg = BagType.objects.create(
                pk=31,
                name='Large Veg',
                tag_color='Blue',
            )
            cls.small_fruit = BagType.objects.create(
                pk=32,
                name='Small Fruit',
                tag_color='Red',
            )
            cls.customer1 = Customer.objects.create_now(pk=41, full_name='One')
            cls.customer2 = Customer.objects.create_now(pk=42, full_name='Two')
            cls.customer2.bag_quantities = {cls.large_veg: 1, cls.small_fruit: 2}
            cls.customer1.collection_point = cls.cp1
            cls.customer2.collection_point = cls.cp1
        with freezegun.freeze_time(str(parse_billing_week('2016-06 2').wed)):
            cls.customer1.collection_point = cls.cp2
            cls.customer2.collection_point = cls.cp2
        with freezegun.freeze_time(str(parse_billing_week('2016-06 3').wed)):
            cls.customer1.collection_point = cls.cp3
            cls.customer2.collection_point = cls.cp3

    def check_lookups(self, result):
        self.assertEqual(
            tuple(result['bag_types']),
            (
                self.large_veg,
                self.small_fruit,
            )
        )

    def strip_result(self, result):
        for collection_point in result:
            del result[collection_point]['user_totals_by_category']
            del result[collection_point]['holiday_bag_total']
            del result[collection_point]['collecting_bag_totals_by_type']
            del result[collection_point]['collecting_bag_total']
        return result

    def test_packing_list(self):
        customers = OrderedDict([
            (
                self.customer1,
                {
                    'holiday': False,
                    'bags': {self.large_veg: 0, self.small_fruit: 0},
                    'new': False,
                }
            ),
            (
                self.customer2,
                {
                    'holiday': False,
                    'bags': {self.large_veg: 1, self.small_fruit: 2},
                    'new': False,
                }
            ),
        ])
        # Test in the week while the data was collected, should get nothing
        result = packing_list(
            CollectionPoint.objects.all(),
            parse_billing_week('2016-06 1')
        )
        self.check_lookups(result)
        expected = OrderedDict()
        self.assertEqual(
            result['billing_week'],
            parse_billing_week('2016-06 1'),
        )
        self.assertEqual(self.strip_result(result['packing_list']), expected)
        # Test in the week after (both in collection point 21)
        result = packing_list(
            CollectionPoint.objects.all(),
            parse_billing_week('2016-06 2')
        )
        self.check_lookups(result)
        self.assertEqual(
            result['billing_week'],
            parse_billing_week('2016-06 2'),
        )
        expected = OrderedDict([(self.cp1, {'customers': customers})])
        self.assertEqual(self.strip_result(result['packing_list']), expected)
        # Test in the last week (should be collection point 22)
        result = packing_list(
            CollectionPoint.objects.all(),
            parse_billing_week('2016-06 3'),
        )
        self.check_lookups(result)
        self.assertEqual(
            result['billing_week'],
            parse_billing_week('2016-06 3'),
        )
        expected = OrderedDict([(self.cp2, {'customers': customers})])
        self.assertEqual(self.strip_result(result['packing_list']), expected)
        # Test in the last week (should be collection point 23)
        result = packing_list(
            CollectionPoint.objects.all(),
            parse_billing_week('2016-06 4'),
        )
        self.check_lookups(result)
        self.assertEqual(
            result['billing_week'],
            parse_billing_week('2016-06 4'),
        )
        expected = OrderedDict([(self.cp3, {'customers': customers})])
        self.assertEqual(self.strip_result(result['packing_list']), expected)

    def test_distinct_on_subquery(self):
        ccpcs = (
            CustomerCollectionPointChange.objects
            .order_by('customer', '-changed')
            .filter(
                changed_in_billing_week__lte=parse_billing_week('2016-06 2')
            )
            .distinct('customer')
        )
        qs = CustomerCollectionPointChange.objects.filter(
            id__in=ccpcs, customer__full_name='Two')
        self.assertEqual(
            [
                (change.customer.full_name, change.collection_point.name)
                for change in qs
            ],
            [('Two', 'Second')]
        )

class CountingUserTestCase(TransactionTestCase):
    """
    In this case, we're actually testing that our fixtures have a
    sufficiently high primary key to start with, so we can import old users
    from the older Blue World app without their ids clashing
    """
    fixtures = ['../data/user.json']

    def setUp(self):
        self.users = models.User.objects.all()

    def testStartingCountIsHighEnough(self):
        for u in self.users:
            self.assertGreater(u.pk, 10000)

    def testNewUsersStartwithHighIdsAsWell(self):
        self.users = models.User.objects.all()
        m = models.User.objects.create(
            email="foo@bar.com",
            password="sekrit",
            username="new_user"
        )
        self.assertGreater(m.pk, 10000)
