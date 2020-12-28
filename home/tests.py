from django.test import TestCase
from home.models import reason_unapproved, reason_approved

# Create your tests here.


class Reasons_upapproved_test(TestCase):
    def test(self):
        reason_unapproved.objects.create(
            reason="a simple unapproved reason",
            email="email@email,com",
            display_name="null",
        )


class reasons_approved_test(TestCase):
    def test(self):
        reason_approved.objects.create(
            reason="a simple approved reason",
            email="email@email,com",
            display_name="null",
        )