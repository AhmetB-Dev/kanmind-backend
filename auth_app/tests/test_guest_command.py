from django.core.management import call_command
from django.test import TestCase

from auth_app.models import User
from auth_app.management.commands.create_guest_user import GUEST_EMAIL


class GuestCommandTests(TestCase):
    def test_guest_user_is_created(self):
        call_command("create_guest_user")

        self.assertTrue(User.objects.filter(email=GUEST_EMAIL).exists())

    def test_guest_user_is_not_created_twice(self):
        call_command("create_guest_user")
        call_command("create_guest_user")

        guest_count = User.objects.filter(email=GUEST_EMAIL).count()
        self.assertEqual(guest_count, 1)
