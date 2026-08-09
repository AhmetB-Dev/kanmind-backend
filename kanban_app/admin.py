from django.contrib import admin
from .models import Board, Task

from .models import Board


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "owner"]
    search_fields = ["title", "owner__email"]
    filter_horizontal = ["members"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "board",
        "status",
        "priority",
        "assignee",
        "reviewer",
        "due_date",
    ]
    list_filter = ["status", "priority"]
    search_fields = ["title", "description"]
