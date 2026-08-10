"""Django admin configuration for the custom user model."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Configure user search, display, and editing in Django admin."""

    ordering = ["email"]
    list_display = ["email", "fullname", "is_staff", "is_active"]
    search_fields = ["email", "fullname"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("fullname",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "fullname", "password1", "password2"),
            },
        ),
    )
