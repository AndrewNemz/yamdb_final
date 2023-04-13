from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            return user.is_admin
        if request.method in permissions.SAFE_METHODS:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in permissions.SAFE_METHODS:
            return True
        if user.is_authenticated:
            return user.is_admin
        return False


class IsAdminOrModeratorOrAuthorOrReadOnly(permissions.BasePermission):
    """
    user only has object permission if admin, moderator or author of object
    """

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                or request.method in permissions.SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (request.user.is_admin
                or request.user.is_moderator
                or obj.author == request.user)
