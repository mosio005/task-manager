from rest_framework.permissions import BasePermission


class TaskOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class CommentOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

