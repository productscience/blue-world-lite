import factory
import uuid

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone

from factory.django import DjangoModelFactory
from faker import Factory

from billing_week import get_billing_week
from . import models

fake = Factory.create()

class UserFactory(DjangoModelFactory):

    class Meta:
        model = get_user_model()


class CustomerFactory(DjangoModelFactory):

    class Meta:
        model = models.Customer

    full_name = factory.Faker('name')
    nickname = factory.LazyAttribute(lambda obj: obj.full_name.split(' ')[0])
    mobile = factory.Faker('phone_number')

    created = factory.LazyFunction(timezone.now)
    created_in_billing_week = factory.LazyAttribute(lambda obj: str(
        get_billing_week(obj.created)))

    user = factory.SubFactory(
        UserFactory,
        username=factory.SelfAttribute('..nickname'),
        email=factory.LazyAttribute(lambda u: "{}@example.com".format(u.username)))

class BagTypeCostChangeFactory(DjangoModelFactory):

    class Meta:
        model = models.BagTypeCostChange

class BagTypeFactory(DjangoModelFactory):

    class Meta:
        model = models.BagType

    name = "Large Veg Bag"
    tag_color = "green"

    # TODO we can't set this in the normal factory, because we don't have a saved
    # bag type at this point
    # weekly_costBagTypeCostChangeFactory
    # weekly_cost = Decimal(16.25)

class CollectionPointFactory(DjangoModelFactory):

    class Meta:
        model = models.CollectionPoint

    name = factory.Faker('company')
    location = factory.Faker('address')

class AccountStatusChangeFactory(DjangoModelFactory):

    class Meta:
        model = models.AccountStatusChange

    changed = factory.LazyFunction(timezone.now)
    changed_in_billing_week = factory.LazyAttribute(
        lambda obj: str(get_billing_week(obj.changed)))

    status = models.AccountStatusChange.AWAITING_DIRECT_DEBIT

class GoCardlessMandateFactory(DjangoModelFactory):

    class Meta:
        model = models.BillingGoCardlessMandate

    session_token = session_token = str(uuid.uuid4())
    gocardless_redirect_flow_id = str(uuid.uuid4())
    gocardless_mandate_id = str(uuid.uuid4())

    created = factory.LazyFunction(timezone.now)
    created_in_billing_week = factory.LazyAttribute(
        lambda obj: str(get_billing_week(obj.created)))


class CompleteGoCardlessMandateFactory(GoCardlessMandateFactory):

    completed = factory.LazyFunction(timezone.now)
    completed_in_billing_week = factory.LazyAttribute(
        lambda obj: str(get_billing_week(obj.completed)))




class SignedUpCustomerFactory(CustomerFactory):
    pass
        # like a normal customer, but has a collection point and an order set,
        # and a status change


class ConfirmedCustomerFactory(DjangoModelFactory):
    pass
        # like a signed up customer, but has a collection point, order set, a status change,
        # and a mandate
