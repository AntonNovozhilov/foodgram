from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    '''Права доступа для администратора или для чтения.'''
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_staff)

class OwnerPermission(permissions.BasePermission):
    '''Права доступа для владельца.'''
    def has_permission(self, request, view):
        return (request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user)

class IsAuthenticatedorCreate(permissions.BasePermission):
    '''Права доступа для аутентифицированного.'''
    def has_permission(self, request, view):
        return (request.method == 'POST' or request.user.is_authenticated)
    