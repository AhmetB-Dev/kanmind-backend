"""API views and viewsets for KanMind board workflows."""

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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


class CommentDeleteView(GenericAPIView):
    """Delete a comment when requested by its author."""

    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def delete(self, request, task_id, comment_id):
        """Delete the requested comment after object permission checks."""
        comment = self._get_comment(task_id, comment_id)
        self.check_object_permissions(request, comment)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _get_comment(self, task_id, comment_id):
        """Return the comment only when it belongs to the requested task."""
        return get_object_or_404(
            Comment,
            pk=comment_id,
            task_id=task_id,
        )


class TaskCreateView(GenericAPIView):
    """Create tasks on boards accessible to the authenticated user."""

    serializer_class = TaskCreateSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]

    def post(self, request):
        """Validate board access and create a task."""
        self._check_board_access(request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _check_board_access(self, request):
        """Run board-level permissions before serializer validation."""
        board_id = request.data.get("board")
        if board_id is None:
            return
        board = get_object_or_404(Board, pk=board_id)
        self.check_object_permissions(request, board)


class ReviewingTasksView(GenericAPIView):
    """List tasks where the authenticated user is the reviewer."""

    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return tasks assigned to the current user for review."""
        tasks = Task.objects.filter(reviewer=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class TaskDetailView(GenericAPIView):
    """Update or delete a single task using action-specific permissions."""

    queryset = Task.objects.all()
    serializer_class = TaskUpdateSerializer

    def get_permissions(self):
        """Use stricter permissions for task deletion."""
        permission_classes = [IsAuthenticated]
        if self.request.method == "DELETE":
            permission_classes.append(IsTaskCreatorOrBoardOwner)
        else:
            permission_classes.append(IsTaskBoardMember)
        return [permission() for permission in permission_classes]

    def patch(self, request, *args, **kwargs):
        """Apply a partial update to an accessible task."""
        task = self.get_object()
        serializer = self.get_serializer(
            task,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        """Delete a task when the caller has deletion permission."""
        task = self.get_object()
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssignedToMeView(GenericAPIView):
    """List tasks assigned to the authenticated user."""

    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return tasks where the current user is the assignee."""
        tasks = Task.objects.filter(assignee=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


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


class TaskCommentsView(GenericAPIView):
    """List and create comments for an accessible task."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMember]

    def get(self, request, task_id):
        """Return task comments in chronological order."""
        task = self._get_task(task_id)
        comments = task.comments.all()
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, task_id):
        """Create a comment authored by the authenticated user."""
        task = self._get_task(task_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task=task, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _get_task(self, task_id):
        """Return the task after board-access permission checks."""
        task = get_object_or_404(Task, pk=task_id)
        self.check_object_permissions(self.request, task)
        return task
