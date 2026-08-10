"""Object-level permissions for boards, tasks, and comments."""

from rest_framework.permissions import BasePermission


class IsBoardMemberOrOwner(BasePermission):
    """Allow access to a board owner or one of its members."""

    def has_object_permission(self, request, view, obj):
        """Return whether the current user can access the board."""
        is_owner = obj.owner == request.user
        is_member = obj.members.filter(pk=request.user.pk).exists()
        return is_owner or is_member


class IsBoardOwner(BasePermission):
    """Restrict an operation to the board owner."""

    def has_object_permission(self, request, view, obj):
        """Return whether the current user owns the board."""
        return obj.owner == request.user


class IsTaskBoardMember(BasePermission):
    """Allow task access to the board owner or a board member."""

    def has_object_permission(self, request, view, obj):
        """Return whether the current user can access the task's board."""
        board = obj.board
        is_owner = board.owner == request.user
        is_member = board.members.filter(pk=request.user.pk).exists()
        return is_owner or is_member


class IsTaskCreatorOrBoardOwner(BasePermission):
    """Allow task deletion to its creator or the owning board user."""

    def has_object_permission(self, request, view, obj):
        """Return whether the current user may delete the task."""
        return obj.created_by == request.user or obj.board.owner == request.user


class IsCommentAuthor(BasePermission):
    """Restrict comment deletion to the original author."""

    def has_object_permission(self, request, view, obj):
        """Return whether the current user authored the comment."""
        return obj.author == request.user
