"""
The DB user needs permission to create the test_blueworld database:

::

    ALTER USER blueworld CREATEDB;
"""

from decimal import Decimal
from pprint import pprint
from django.test import TestCase
from join.admin import packing_list
from join.models import CollectionPoint, CustomerCollectionPointChange, CustomerOrderChange
from join.models import Customer, BagType, LineItem, Skip, PaymentStatusChange
from join.models import Payment, AccountStatusChange
from billing_week import get_billing_week, parse_billing_week
from django.utils import timezone
import freezegun
import pytz
import datetime
from collections import OrderedDict


from unittest import TestCase as _TC
_TC.maxDiff = None
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


# Billing week needs last week and first week of month
# Need a class BillingMonth


class TestLineItemRun(TestCase):
    '''
    Cases:

    * User joins with collections left in the month
    * User joins without collections

    * Line item runner doesn't create entries for:
      * Customers that aren't ACTIVE
      * The first month after a user was created (because they will already be billed).

    In July 2016, Sunday 24th at 3pm is the cutoff for the last billing week.

    XXX Can't collect bags if not ACTIVE
    XXX Probably lots of other cases that need thinking about with the team before GoLive
    XXX What happens if they activate late
    '''
    #@classmethod
    def setUp(self):
        # Freeze time in UTC
        with freezegun.freeze_time('2015-11-01 00:00', tick=False):
            bag_type1 = BagType.objects.create(name='Large Bag')
            bag_type1.weekly_cost=Decimal('8.00')
            bag_type2 = BagType.objects.create(name='Small Bag')
            bag_type2.weekly_cost=Decimal('5.52')
        # In billing week 3, just before the start of billing week 4 (the last of the month)
        with freezegun.freeze_time('2015-11-22 11:50', tick=False):
            # Customer signs up with one collection left in July
            now3 = timezone.now()
            bw3 = get_billing_week(now3)
            print('Creating Customer One in {}'.format(bw3))
            self.customer1 = Customer.objects.create_now(full_name='Customer One')
            self.customer1._set_bag_quantities({bag_type1: 1, bag_type2: 2}, reason='JOIN')
            payment = Payment(
                customer=self.customer1,
                gocardless_mandate_id='xxx',
                amount=Decimal('19.04'),
                reason=Payment.JOIN_WITH_COLLECTIONS_AVAILABLE,
                gocardless_payment_id='xxx',
                created=now3,
                created_in_billing_week=str(bw3),
            )
            payment.save()
            payment_status_change = PaymentStatusChange(
                changed=now3,
                changed_in_billing_week=str(bw3),
                status='xxx',
                payment=payment,
            )
            payment_status_change.save()
            for x in range(1):
                li = LineItem(
                    payment=payment,
                    created=now3,
                    created_in_billing_week=bw3,
                    # The changes are from now:
                    bill_against=str(bw3.next()),
                    customer=self.customer1,
                    amount=Decimal('19.04'),
                    reason=LineItem.NEW_JOINER
                )
                li.save()
            account_status_change = AccountStatusChange(
                changed=now3,
                changed_in_billing_week=str(bw3),
                customer=self.customer1,
                status=AccountStatusChange.ACTIVE,
            )
            account_status_change.save()
        # Just after the deadline for billing week 4 => No billing dates left this month
        with freezegun.freeze_time('2015-11-22 15:10', tick=False):
            # Customer signs up with no collections left in July
            now4 = timezone.now()
            bw4 = get_billing_week(now4)
            print('Creating Customer Two in {}'.format(bw4))
            assert bw4 == bw3.next()
            self.customer2 = Customer.objects.create_now(full_name='Customer Two')
            self.customer2._set_bag_quantities({bag_type1: 1, bag_type2: 3}, reason='JOIN')
            account_status_change = AccountStatusChange(
                changed=now4,
                changed_in_billing_week=str(bw4),
                customer=self.customer2,
                status=AccountStatusChange.ACTIVE,
            )
            account_status_change.save()
            # Customer signs up but never completes GoCardless
            print('Creating Customer Three in {}'.format(bw4))
            self.customer3 = Customer.objects.create_now(full_name='Customer Three')
            self.customer3._set_bag_quantities({bag_type1: 1, bag_type2: 3}, reason='JOIN')
            account_status_change = AccountStatusChange(
                changed=now4,
                changed_in_billing_week=str(bw4),
                customer=self.customer3,
                status=AccountStatusChange.AWAITING_DIRECT_DEBIT,
            )
            account_status_change.save()

        # We change Customer 2's order (from 3 to 2 bag types) and set some skip weeks:
        with freezegun.freeze_time('2015-12-09 15:10', tick=False): # Change in billing week 2, takes effect billing week 3
            now2 = timezone.now()
            bw2 = get_billing_week(now2)
            print('Changing Customer Two in {}'.format(bw2))
            self.customer2._set_bag_quantities({bag_type1: 1, bag_type2: 2}, reason='JOIN')
        skip = Skip(customer=self.customer2, billing_week=bw2)
        skip.save()
        # Skip the same week as the order change above
        skip = Skip(customer=self.customer2, billing_week=parse_billing_week('2015-12 3'))
        skip.save()


    def test_run(self): 
        # Nothing happens in November, the customers didn't exist
        print('+++', 2015, 11, '+++')
        line_items_by_customer = LineItem.create_line_items(2015, 11)
        self.assertEqual(line_items_by_customer, {})
        payment_by_customer = Payment.create_payments(2015, 11)
        self.assertEqual(payment_by_customer, {})



        # We add entries for next week
        # We refund for last month
        # We ignore customer3 due to no Direct Debit
        print('+++', 2015, 12, '+++')
        line_items_by_customer = LineItem.create_line_items(2015, 12)
        self.assertEqual(tuple(line_items_by_customer.keys()), (self.customer1, self.customer2))
        self.assertEqual(
            [
                ('2015-12 1', LineItem.REGULAR, Decimal('19.04')),
                ('2015-12 2', LineItem.REGULAR, Decimal('19.04')),
                ('2015-12 3', LineItem.REGULAR, Decimal('19.04')),
                ('2015-12 4', LineItem.REGULAR, Decimal('19.04')),
                ('2015-12 5', LineItem.REGULAR, Decimal('19.04')),
            ],
            [(str(li.bill_against), li.reason, li.amount) for li in line_items_by_customer[self.customer1]],
        )
        self.assertEqual(
            [
                ('2015-12 1', LineItem.REGULAR, Decimal('24.56')),
                ('2015-12 2', LineItem.REGULAR, Decimal('24.56')),
                ('2015-12 3', LineItem.REGULAR, Decimal('24.56')),
                ('2015-12 4', LineItem.REGULAR, Decimal('24.56')),
                ('2015-12 5', LineItem.REGULAR, Decimal('24.56')),
            ],
            [(str(li.bill_against), li.reason, li.amount) for li in line_items_by_customer[self.customer2]],
        )
        pprint(line_items_by_customer)
        payment_by_customer = Payment.create_payments(2015, 12)
        self.assertEqual(tuple(payment_by_customer.keys()), (self.customer1, self.customer2))
        self.assertEqual(
            Decimal('95.20'),
            payment_by_customer[self.customer1].amount,
        )
        self.assertEqual(
            Decimal('122.80'),
            payment_by_customer[self.customer2].amount,
        )

        # We add entries for next week
        # We refund for last month
        # We ignore customer3 due to no Direct Debit
        print('+++', 2016, 1, '+++')
        line_items_by_customer = LineItem.create_line_items(2016, 1)
        self.assertEqual(tuple(line_items_by_customer.keys()), (self.customer1, self.customer2))
        self.assertEqual(
            [
                ('2016-01 1', LineItem.REGULAR, Decimal('19.04')),
                ('2016-01 2', LineItem.REGULAR, Decimal('19.04')),
                ('2016-01 3', LineItem.REGULAR, Decimal('19.04')),
                ('2016-01 4', LineItem.REGULAR, Decimal('19.04')),
            ],
            [(str(li.bill_against), li.reason, li.amount) for li in line_items_by_customer[self.customer1]],
        )

        self.assertEqual(
            [
                ('2015-12 2', LineItem.SKIP_REFUND, Decimal('-24.56')),
                ('2015-12 3', LineItem.ORDER_CHANGE_ADJUSTMENT, Decimal('-5.52')),
                ('2015-12 3', LineItem.SKIP_REFUND, Decimal('-19.04')),
                ('2015-12 4', LineItem.ORDER_CHANGE_ADJUSTMENT, Decimal('-5.52')),
                ('2015-12 5', LineItem.ORDER_CHANGE_ADJUSTMENT, Decimal('-5.52')),

                ('2016-01 1', LineItem.REGULAR, Decimal('19.04')),
                ('2016-01 2', LineItem.REGULAR, Decimal('19.04')),
                ('2016-01 3', LineItem.REGULAR, Decimal('19.04')),
                ('2016-01 4', LineItem.REGULAR, Decimal('19.04')),
            ],
            [(str(li.bill_against), li.reason, li.amount) for li in line_items_by_customer[self.customer2]],
        )
        pprint(line_items_by_customer)
        payment_by_customer = Payment.create_payments(2016, 1)
        self.assertEqual(tuple(payment_by_customer.keys()), (self.customer1, self.customer2))
        self.assertEqual(
            Decimal('76.16'),
            payment_by_customer[self.customer1].amount,
        )
        self.assertEqual(
            Decimal('16.00'),
            payment_by_customer[self.customer2].amount,
        )


        print('+++', 2016, 2, '+++')
        line_items_by_customer = LineItem.create_line_items(2016, 2)
        self.assertEqual(tuple(line_items_by_customer.keys()), (self.customer1, self.customer2))
        self.assertEqual(
            [
                ('2016-02 1', LineItem.REGULAR, Decimal('19.04')),
                ('2016-02 2', LineItem.REGULAR, Decimal('19.04')),
                ('2016-02 3', LineItem.REGULAR, Decimal('19.04')),
                ('2016-02 4', LineItem.REGULAR, Decimal('19.04')),
            ],
            [(str(li.bill_against), li.reason, li.amount) for li in line_items_by_customer[self.customer1]],
        )

        self.assertEqual(
            [
                ('2016-02 1', LineItem.REGULAR, Decimal('19.04')),
                ('2016-02 2', LineItem.REGULAR, Decimal('19.04')),
                ('2016-02 3', LineItem.REGULAR, Decimal('19.04')),
                ('2016-02 4', LineItem.REGULAR, Decimal('19.04')),
            ],
            [(str(li.bill_against), li.reason, li.amount) for li in line_items_by_customer[self.customer2]],
        )
        pprint(line_items_by_customer)
        payment_by_customer = Payment.create_payments(2016, 2)
        self.assertEqual(tuple(payment_by_customer.keys()), (self.customer1, self.customer2))
        self.assertEqual(
            Decimal('76.16'),
            payment_by_customer[self.customer1].amount,
        )
        self.assertEqual(
            Decimal('76.16'),
            payment_by_customer[self.customer2].amount,
        )
