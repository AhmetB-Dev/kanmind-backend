from django.core.management.base import BaseCommand

from auth_app.models import User


GUEST_EMAIL = "guest@kanmind.example"
GUEST_PASSWORD = "GuestDemo123!"
GUEST_FULLNAME = "Guest User"


class Command(BaseCommand):
    help = "Creates the default guest user if it does not exist."

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            email=GUEST_EMAIL,
            defaults={"fullname": GUEST_FULLNAME},
        )
        if not created:
            self.stdout.write("Guest user already exists.")
            return
        self._set_password(user)

    def _set_password(self, user):
        user.set_password(GUEST_PASSWORD)
        user.save()
        self.stdout.write(self.style.SUCCESS("Guest user created."))
