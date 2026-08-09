from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from kanban_app.models import Board

from .permissions import IsBoardMemberOrOwner, IsBoardOwner
from .serializers import (
    BoardDetailSerializer,
    BoardSerializer,
    BoardUpdateSerializer,
)


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
