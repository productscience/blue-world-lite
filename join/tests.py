from django.contrib.auth import models
from django.test import TransactionTestCase
# from join.models import Customer

class CountingUserTestCase(TransactionTestCase):
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
