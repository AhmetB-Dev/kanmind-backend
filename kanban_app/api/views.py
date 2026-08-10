"""API views and viewsets for KanMind board workflows."""

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    ListCreateAPIView,
    UpdateAPIView,
)
from rest_framework.mixins import DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from kanban_app.models import Board, Comment, Task

from .permissions import (
    IsBoardMemberOrOwner,
    IsBoardOwner,
    IsCommentAuthor,
    IsTaskBoardMember,
    IsTaskCreatorOrBoardOwner,
)
from .serializers import (
    BoardDetailSerializer,
    BoardSerializer,
    BoardUpdateSerializer,
    CommentSerializer,
    TaskCreateSerializer,
    TaskListSerializer,
    TaskUpdateSerializer,
)


class CommentDeleteView(DestroyAPIView):
    """Delete a comment when requested by its author."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    lookup_url_kwarg = "comment_id"

    def get_queryset(self):
        """Limit deletion to comments belonging to the requested task."""
        return Comment.objects.filter(task_id=self.kwargs["task_id"])


class TaskCreateView(CreateAPIView):
    """Create tasks on boards accessible to the authenticated user."""

    serializer_class = TaskCreateSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]

    def create(self, request, *args, **kwargs):
        """Check board access before validating and creating the task."""
        self._check_board_access(request)
        return super().create(request, *args, **kwargs)

    def _check_board_access(self, request):
        """Run board-level permissions before serializer validation."""
        board_id = request.data.get("board")
        if board_id is None:
            return
        board = get_object_or_404(Board, pk=board_id)
        self.check_object_permissions(request, board)


class ReviewingTasksView(ListAPIView):
    """List tasks where the authenticated user is the reviewer."""

    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return tasks assigned to the current user for review."""
        return Task.objects.filter(reviewer=self.request.user)


class TaskDetailView(DestroyModelMixin, UpdateAPIView):
    """Update or delete a task with action-specific permissions."""

    queryset = Task.objects.all()
    serializer_class = TaskUpdateSerializer
    http_method_names = ["patch", "delete", "head", "options"]

    def get_permissions(self):
        """Use stricter permissions for task deletion."""
        permission_classes = [IsAuthenticated]
        if self.request.method == "DELETE":
            permission_classes.append(IsTaskCreatorOrBoardOwner)
        else:
            permission_classes.append(IsTaskBoardMember)
        return [permission() for permission in permission_classes]

    def delete(self, request, *args, **kwargs):
        """Delete the task through DRF's destroy mixin."""
        return self.destroy(request, *args, **kwargs)


class AssignedToMeView(ListAPIView):
    """List tasks assigned to the authenticated user."""

    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return tasks where the current user is the assignee."""
        return Task.objects.filter(assignee=self.request.user)


class BoardViewSet(ModelViewSet):
    """Provide board CRUD operations with action-specific responses."""

    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        """Return only boards visible to the authenticated user when listing."""
        if self.action != "list":
            return Board.objects.all()
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def get_permissions(self):
        """Choose board permissions based on the requested action."""
        permission_classes = [IsAuthenticated]
        if self.action == "destroy":
            permission_classes.append(IsBoardOwner)
        elif self.action in ["retrieve", "update", "partial_update"]:
            permission_classes.append(IsBoardMemberOrOwner)
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Select the response shape required for each board action."""
        if self.action == "retrieve":
            return BoardDetailSerializer
        if self.action in ["update", "partial_update"]:
            return BoardUpdateSerializer
        return BoardSerializer


class TaskCommentsView(ListCreateAPIView):
    """List and create comments for an accessible task."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMember]

    def get_queryset(self):
        """Return comments for the requested accessible task."""
        return self._get_task().comments.all()

    def create(self, request, *args, **kwargs):
        """Check task access before validating a new comment."""
        self.task = self._get_task()
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Attach the authenticated user and requested task."""
        serializer.save(task=self.task, author=self.request.user)

    def _get_task(self):
        """Return the task after board-access permission checks."""
        task = get_object_or_404(Task, pk=self.kwargs["task_id"])
        self.check_object_permissions(self.request, task)
        return task
