from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AssignedToMeView,
    BoardViewSet,
    ReviewingTasksView,
    TaskCreateView,
    TaskDetailView,
    CommentDeleteView,
    TaskCommentsView,
)

router = DefaultRouter()
router.register("boards", BoardViewSet, basename="board")

urlpatterns = [
    path("tasks/", TaskCreateView.as_view(), name="task-create"),
    path(
        "tasks/assigned-to-me/",
        AssignedToMeView.as_view(),
        name="assigned-to-me",
    ),
    path(
        "tasks/<int:pk>/",
        TaskDetailView.as_view(),
        name="task-detail",
    ),
    path(
        "tasks/reviewing/",
        ReviewingTasksView.as_view(),
        name="task-reviewing",
    ),
    path(
        "tasks/<int:task_id>/comments/",
        TaskCommentsView.as_view(),
        name="task-comments",
    ),
    path(
        "tasks/<int:task_id>/comments/<int:comment_id>/",
        CommentDeleteView.as_view(),
        name="comment-delete",
    ),
]
urlpatterns += router.urls
