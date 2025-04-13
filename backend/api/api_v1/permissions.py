from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Права доступа для администратора или только для чтения."""

    def has_permission(self, request, view):
        """Разрешить доступ, если метод безопасный или пользователь — админ."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
        )


class OwnerPermission(permissions.BasePermission):
    """Права доступа только для владельца объекта."""

    def has_permission(self, request, view):
        """Разрешить доступ аутентифицированному пользователю."""
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Разрешить доступ, если пользователь является автором объекта."""
        return obj.author == request.user


class IsAuthenticatedorCreate(permissions.BasePermission):
    """Права для аутентифицированных или на создание."""

    def has_permission(self, request, view):
        """Разрешить POST или доступ аутентифицированному пользователю."""
        return request.method == 'POST' or request.user.is_authenticated
