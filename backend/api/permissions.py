from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_staff)

class OwnerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return True
    
    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user)
    
class IsAuthenticatedorCreate(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method == 'POST' or request.user.is_authenticated)
    