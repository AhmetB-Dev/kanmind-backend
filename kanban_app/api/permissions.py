from rest_framework.permissions import BasePermission


class IsBoardMemberOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        is_owner = obj.owner == request.user
        is_member = obj.members.filter(pk=request.user.pk).exists()
        return is_owner or is_member


class IsBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
