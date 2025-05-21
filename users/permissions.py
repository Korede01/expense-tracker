from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """Allows access only to admin users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Admin'

class IsUser(BasePermission):
    """Allows access only to regular (non-admin, non-affiliator) users."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'User')
