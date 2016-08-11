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
from join.helper import calculate_weekly_fee
from join.models import Customer, BagType, LineItem, Skip, PaymentStatusChange
from join.models import LineItemRun, Payment, PaymentRun, AccountStatusChange
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
        line_items_by_customer = create_line_items(2015, 11)
        self.assertEqual(line_items_by_customer, {})
        payment_by_customer = create_payments(2015, 11)
        pprint(payment_by_customer)

        # We add entries for next week
        # We refund for last month
        # We ignore customer3 due to no Direct Debit
        print('+++', 2015, 12, '+++')
        line_items_by_customer = create_line_items(2015, 12)
        pprint(line_items_by_customer)
        payment_by_customer = create_payments(2015, 12)
        pprint(payment_by_customer)
        # self.assertEqual(line_items_by_customer, {})
        # We add entries for next week
        # We refund for last month
        # We ignore customer3 due to no Direct Debit
        print('+++', 2016, 1, '+++')
        line_items_by_customer = create_line_items(2016, 1)
        pprint(line_items_by_customer)
        payment_by_customer = create_payments(2016, 1)
        pprint(payment_by_customer)
        # self.assertEqual(line_items_by_customer, {})

        print('+++', 2016, 2, '+++')
        line_items_by_customer = create_line_items(2016, 2)
        pprint(line_items_by_customer)
        payment_by_customer = create_payments(2016, 2)
        pprint(payment_by_customer)
        # self.assertEqual(line_items_by_customer, {})
        # total = sum([li.amount for li in line_items_by_customer[self.customer1]])
        # print('Total adjustment:', total)
        # # Note: We wouldn't get this in real life, since the joiner would have paid already.
        # self.assertEqual(len(line_items_by_customer[self.customer1]), 6)
        # self.assertEqual(total, Decimal('98.24'))
        # self.assertEqual(payment_by_customer[self.customer1].amount, Decimal('98.24'))
        # with freezegun.freeze_time('2016-09-04 14:10', tick=False):
        #     payment_by_customer = create_payments(2016, 9)
        #     pprint(payment_by_customer)
        # self.assertEqual(payment_by_customer[self.customer1].amount, Decimal('98.24'))


def create_line_items(year, month, start_customer=0):
    '''
    We run this immediately after the billing date affecting the first billing
    week of the month.  So, if given 2016, 8 to run a bill in advance for
    August, the code should be run on Sunday 31 July 2016 just after 3pm GMT.

    We will create line items for August, and adjustments due during July.


    XXX What happens if someone leaves - should we automatically set skip weeks
        until the end of the month -> Then Leave status only applies on the month
        following and skip weeks is what causes the refund

    XXX Also need to make sure that collection points don't show up for LEAVEs
    '''
    # e.g. 31st July 2016
    now = timezone.now()
    
    last_run = LineItemRun.objects.order_by('-started')[:1]
    if last_run:
        assert last_run[0].started < now, 'The last run was in the future'

    line_item_run = LineItemRun.objects.create(
        job_id = 'xxx',
        year = year,
        month = month,
        started = now,
        finished =None,
        start_customer = start_customer or None,
        currently_processing_customer = None,
    )
    line_item_run.save()
    line_items_by_customer = {}
    now_bw = get_billing_week(now)
    # Find the last first billing week of the previous month
    billing_week = future_billing_week = parse_billing_week('{0}-{1:02d} {2}'.format(year, month, 1))
    assert now_bw >= billing_week, 'Cannot run line items for future weeks'
    billing_weeks_next_month = []
    while future_billing_week.month == month:
        billing_weeks_next_month.append(future_billing_week)
        future_billing_week = future_billing_week.next()

    old_billing_week = start = billing_week.prev()
    billing_weeks_last_month = []
    while old_billing_week.month == start.month:
        billing_weeks_last_month.append(old_billing_week)
        old_billing_week = old_billing_week.prev()
    billing_weeks_last_month.reverse()

    print(billing_weeks_last_month)
    print(billing_weeks_next_month)

    # For each customer
    customers = Customer.objects.order_by('pk').filter(created__lt=billing_weeks_next_month[0].start)
    print(customers.all())
    for customer in customers:
        if customer.pk < start_customer:
            continue
        if not line_item_run.start_customer:
            line_item_run.start_customer = customer
        line_item_run.currently_processing_customer = customer
        line_item_run.save()
        print('Processing', customer, customer.account_status_before(billing_weeks_next_month[0].start))


        if customer.account_status not in (AccountStatusChange.AWAITING_DIRECT_DEBIT):
            # For each billing week in the previous month...
            for past_billing_week in billing_weeks_last_month:
                # Look up what the order actually was
                bag_quantities = CustomerOrderChange.as_of(past_billing_week, customer=customer)
                should_have_billed = calculate_weekly_fee(bag_quantities)
                # Look up the line item for that week
                lis = LineItem.objects.filter(
                    customer=customer,
                    bill_against=str(past_billing_week),
                    reason__in=(LineItem.REGULAR, LineItem.NEW_JOINER),
                ).all()
                assert len(lis) <= 1
                if len(lis) == 1:
                    billed = lis[0].amount 
                else:
                    billed = 0
                print('Billed:', billed, 'Should have billed:', should_have_billed)
                correction = should_have_billed - billed        
                if correction != 0:
                    cli = LineItem(
                        amount=correction,
                        created=now,
                        created_in_billing_week=now_bw,
                        customer=customer,
                        bill_against=str(past_billing_week),
                        reason=LineItem.ORDER_CHANGE_ADJUSTMENT,
                    )
                    cli.save()
                    line_items_by_customer.setdefault(customer, []).append(cli)
                # If there is a skip week, refund the cost of the new order
                skips = Skip.objects.filter(customer=customer, billing_week=past_billing_week).all()
                assert len(skips) <= 1
                if len(skips): 
                    print('Skips:', skips, past_billing_week, -should_have_billed)
                    cli = LineItem(
                        amount=-should_have_billed,
                        created=now,
                        created_in_billing_week=now_bw,
                        customer=customer,
                        bill_against=str(past_billing_week),
                        reason=LineItem.SKIP_REFUND,
                    )
                    cli.save()
                    line_items_by_customer.setdefault(customer, []).append(cli)
        # If the customer has left, or not set up don't bill them:
        if customer.account_status_before(billing_weeks_next_month[0].start) not in (AccountStatusChange.AWAITING_DIRECT_DEBIT, AccountStatusChange.LEFT):
            # For each billing week in the next month, add a line item to the order
            print('Adding in line items for next months order')
            next_month_bag_quantities = CustomerOrderChange.as_of(
                billing_weeks_next_month[0], 
                customer=customer,
            )
            weekly_cost = calculate_weekly_fee(next_month_bag_quantities)
            for future_billing_week in billing_weeks_next_month:
                li = LineItem(
                    amount=weekly_cost,
                    created=now,
                    created_in_billing_week=now_bw,
                    customer=customer,
                    bill_against=str(future_billing_week),
                    reason=LineItem.REGULAR,
                )
                li.save()
                line_items_by_customer.setdefault(customer, []).append(li)
    return line_items_by_customer

   
def create_payments(year, month, start_customer=0):
    now = timezone.now()

    # If the account is in credit after taking the line items into account, it will be ignored this month.
    # Upcoming line items can show on the billing history page.
    now_bw = get_billing_week(now)
    # Find the last deadline of the month
    billing_week = parse_billing_week('{0}-{1:02d} {2}'.format(year, month, 1))
    assert now_bw >= billing_week, 'Cannot create payments in the future'

    last_run = PaymentRun.objects.order_by('-started')[:1]
    if last_run:
        assert last_run[0].started < now, 'The last run was in the future'

    payment_run = PaymentRun.objects.create(
        job_id = 'xxx',
        year = year,
        month = month,
        started = now,
        finished =None,
        start_customer = start_customer or None,
        currently_processing_customer = None,
    )
    payment_run.save()
    payment_by_customer = {}
    # billing_weeks_this_month = []
    # while billing_week.month == month:
    #     billing_weeks_this_month.append(billing_week)
    #     billing_week = billing_week.next()
    # print(billing_weeks_this_month)
    # For each customer
    for customer in Customer.objects.order_by('pk'):
        if customer.pk < start_customer:
            print('Skip')
            continue
        if not payment_run.start_customer:
            payment_run.start_customer = customer
        payment_run.currently_processing_customer = customer
        payment_run.save()
        print(customer)
        # Look at *all* line items that don't have a payment and create the payment object for them
        line_items = LineItem.objects.filter(payment=None, customer=customer)
        total = Decimal(0)
        for line_item in line_items:
            total += line_item.amount
        print(total)
        # If the account is in credit after taking the line items into account, it will be ignored this month.
        if total > 0:
            mandate_id = 'xxx', #customer.gocardless_current_mandate.gocardless_mandate_id
            payment_response_id = 'xxx'
            payment_response_status = 'xxx'
            payment = Payment(
                customer=customer,
                gocardless_mandate_id=mandate_id,
                amount=total,
                reason=Payment.MONTHLY_INVOICE,
                gocardless_payment_id=payment_response_id,
                created=now,
                created_in_billing_week=str(now_bw),
            )
            payment.save()
            payment_status_change = PaymentStatusChange(
                changed=now,
                changed_in_billing_week=str(now_bw),
                status=payment_response_status,
                payment=payment,
            )
            payment_status_change.save()
            for line_item in line_items:
                line_item.payment = payment
                line_item.save()
            payment_by_customer[customer] = payment
    return payment_by_customer
    # Upcoming line items can show on the billing history page.
