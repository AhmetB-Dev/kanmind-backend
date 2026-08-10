"""Django admin configuration for KanMind domain models."""

from django.contrib import admin

from .models import Board, Comment, Task


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """Configure board management in Django admin."""

    list_display = ("id", "title", "owner")
    search_fields = ("title", "owner__email")
    filter_horizontal = ("members",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Configure task management in Django admin."""

    list_display = ("id", "title", "board", "status", "priority", "due_date")
    list_filter = ("status", "priority")
    search_fields = ("title", "board__title")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Configure comment management in Django admin."""

    list_display = ("id", "task", "author", "created_at")
    search_fields = ("content", "author__email", "task__title")
