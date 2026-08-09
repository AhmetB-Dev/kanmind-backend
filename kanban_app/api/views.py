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
    IsTaskBoardMember,
    IsCommentAuthor,
    IsTaskCreatorOrBoardOwner,
)

from .serializers import (
    BoardDetailSerializer,
    BoardSerializer,
    BoardUpdateSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    CommentSerializer,
    TaskListSerializer,
)


class CommentDeleteView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def delete(self, request, task_id, comment_id):
        comment = self._get_comment(task_id, comment_id)
        self.check_object_permissions(request, comment)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _get_comment(self, task_id, comment_id):
        return get_object_or_404(
            Comment,
            pk=comment_id,
            task_id=task_id,
        )


class TaskCreateView(GenericAPIView):
    serializer_class = TaskCreateSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]

    def post(self, request):
        self._check_board_access(request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _check_board_access(self, request):
        board_id = request.data.get("board")
        if board_id is None:
            return
        board = get_object_or_404(Board, pk=board_id)
        self.check_object_permissions(request, board)


class ReviewingTasksView(GenericAPIView):
    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(reviewer=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class TaskDetailView(GenericAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskUpdateSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method == "DELETE":
            permission_classes.append(IsTaskCreatorOrBoardOwner)
        else:
            permission_classes.append(IsTaskBoardMember)
        return [permission() for permission in permission_classes]

    def patch(self, request, *args, **kwargs):
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
        task = self.get_object()
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssignedToMeView(GenericAPIView):
    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(assignee=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class BoardViewSet(ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def get_queryset(self):
        if self.action != "list":
            return Board.objects.all()

        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def get_permissions(self):
        permissions = [IsAuthenticated]

        if self.action == "destroy":
            permissions.append(IsBoardOwner)
        elif self.action in ["retrieve", "update", "partial_update"]:
            permissions.append(IsBoardMemberOrOwner)

        return [permission() for permission in permissions]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BoardDetailSerializer
        if self.action in ["update", "partial_update"]:
            return BoardUpdateSerializer
        return BoardSerializer


class TaskCommentsView(GenericAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        task = self._get_task(task_id)
        comments = task.comments.all()
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, task_id):
        task = self._get_task(task_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task=task, author=request.user)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def _get_task(self, task_id):
        task = get_object_or_404(Task, pk=task_id)
        self._check_task_access(task)
        return task

    def _check_task_access(self, task):
        user = self.request.user
        board = task.board
        if board.owner == user:
            return
        if board.members.filter(pk=user.pk).exists():
            return
        self.permission_denied(self.request)
