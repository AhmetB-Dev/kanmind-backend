"""Custom manager for the email-based user model."""

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Create regular users and superusers using email as the identifier."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and persist a user with a normalized email address."""
        if not email:
            raise ValueError("Users must have an email address.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create a staff user with superuser permissions."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)
