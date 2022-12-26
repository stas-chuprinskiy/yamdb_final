from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    message = 'Only admin users have access to this resource.'

    def has_permission(self, request, view):
        return request.user.is_admin


class IsAdminOrReadOnly(permissions.BasePermission):
    message = 'Only admin users have access to this resource.'

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin
        )


class IsAdminModeratorAuthorOrReadOnly(permissions.BasePermission):
    message = (
        'Only admin, moderator or author users have access to this resource.'
    )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (
                obj.author == request.user
                or request.user.is_moderator
                or request.user.is_admin
            )
        )
